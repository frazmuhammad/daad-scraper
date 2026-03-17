# scraper.py
"""
Handles the actual scraping of course detail pages.
Uses Selenium to get the list of course links from the search results,
then multi‑threaded requests to scrape each detail page.
"""

import time
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import SCRAPER_DB, MAX_WORKERS, HEADERS, SELENIUM_WAIT, REQUEST_TIMEOUT
from excel_exporter import export_to_excel   # will be used at the end

def init_scraper_db(db_path=SCRAPER_DB):
    """Create the database table for storing courses if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            url TEXT PRIMARY KEY,
            course_name TEXT,
            university TEXT,
            city TEXT,
            admission_req TEXT,
            language_req TEXT,
            deadline TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_scraped_urls(db_path=SCRAPER_DB):
    """Return a set of URLs already present in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM courses")
    urls = {row[0] for row in cursor.fetchall()}
    conn.close()
    return urls

def save_to_db(item, db_path=SCRAPER_DB):
    """Insert a single course record into the database."""
    if "ERROR" in item["Course Name"]:
        return  # don't save failed attempts

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO courses (url, course_name, university, city, admission_req, language_req, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item["URL"], item["Course Name"], item["University"], item["City"],
              item["Admission Req"], item["Language Req"], item["Deadline"]))
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

def get_course_links(search_url, wait_time=SELENIUM_WAIT):
    """
    Use Selenium to load the search results page and extract all course detail links.
    Returns a list of absolute URLs (with #tab_registration appended if missing).
    """
    print("🚀 Opening DAAD Search via Selenium...")
    options = Options()
    options.add_argument("--headless")  # run in background
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(search_url)
        time.sleep(wait_time)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_tags = soup.find_all('a', class_='js-course-detail-link')

        links = []
        for tag in link_tags:
            url = "https://www2.daad.de" + tag['href']
            if "#tab_registration" not in url:
                url += "#tab_registration"
            if url not in links:
                links.append(url)
        return links
    finally:
        driver.quit()

def create_session(headers=HEADERS):
    """Create a requests Session with retry strategy and custom headers."""
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('https://', adapter)
    session.headers.update(headers)
    return session

def scrape_detail_page(url, session, timeout=REQUEST_TIMEOUT):
    """
    Fetch a single course detail page and extract the required fields.
    Returns a dictionary with keys: URL, Course Name, University, City,
    Admission Req, Language Req, Deadline. Returns None on failure.
    """
    try:
        response = session.get(url, timeout=timeout)
        if response.status_code == 403 or "captcha" in response.text.lower():
            return None

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        item = {
            "URL": url,
            "Course Name": "N/A",
            "University": "N/A",
            "City": "N/A",
            "Admission Req": "N/A",
            "Language Req": "N/A",
            "Deadline": "N/A"
        }

        title = soup.find("h2", class_="c-detail-header__title")
        if title:
            item["Course Name"] = title.get_text(strip=True)

        subtitle = soup.find("h3", class_="c-detail-header__subtitle")
        if subtitle:
            parts = subtitle.get_text(strip=True).split("•")
            item["University"] = parts[0].strip() if len(parts) > 0 else "N/A"
            item["City"] = parts[1].strip() if len(parts) > 1 else "N/A"

        reg_div = soup.find("div", id="registration")
        if reg_div:
            for dt in reg_div.find_all("dt"):
                label = dt.get_text(strip=True)
                dd = dt.find_next_sibling("dd")
                val = dd.get_text(separator=" ", strip=True) if dd else "N/A"

                if "Academic admission requirements" in label:
                    item["Admission Req"] = val
                elif "Language requirements" in label:
                    item["Language Req"] = val
                elif "Application deadline" in label:
                    item["Deadline"] = val

        return item
    except Exception:
        # Silently ignore errors (can be logged if needed)
        return None

def run_scraper(search_url, output_excel, db_path=SCRAPER_DB, max_workers=MAX_WORKERS, headers=HEADERS):
    """
    Orchestrate the entire scraping process:
      1. Get all course links from the search results.
      2. Filter out already scraped URLs.
      3. Scrape new detail pages concurrently.
      4. Save to database.
      5. Export to Excel.
    """
    init_scraper_db(db_path)

    all_links = get_course_links(search_url)
    existing_urls = get_scraped_urls(db_path)

    links_to_scrape = [link for link in all_links if link not in existing_urls]
    total_new = len(links_to_scrape)

    if total_new == 0:
        print("✨ Everything is up to date! No new courses to scrape.")
    else:
        print(f"🔍 Found {len(all_links)} total courses. {total_new} are new. Starting scrape...")

        session = create_session(headers)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(scrape_detail_page, url, session) for url in links_to_scrape]

            for count, future in enumerate(futures, 1):
                result = future.result()
                if result:
                    save_to_db(result, db_path)

                if count % 10 == 0:
                    print(f"Progress: {count}/{total_new} new courses processed...")

    # Export to Excel (even if no new courses, we still export existing data)
    export_to_excel(output_excel, db_path)