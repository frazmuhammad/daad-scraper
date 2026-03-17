# config.py
"""
Central configuration file for the DAAD scraper.
Edit these values to change database names, file paths, or scraping behavior.
"""

# Database for filter definitions (created by the separate setup script)
FILTERS_DB = "daad_filters.db"

# Database for storing scraped course data
SCRAPER_DB = "daad_data.db"

# Maximum number of concurrent threads for scraping detail pages
MAX_WORKERS = 10

# HTTP headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# Base URL of the DAAD search (do not change unless the website structure changes)
BASE_URL = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/"

# Default query parameters (limit set high to get all results on one page)
DEFAULT_PARAMS = {
    "cert": "", "admReq": "", "langExamPC": "", "langExamLC": "", "langExamSC": "",
    "degree[]": "", "subjectGroup[]": "", "fos[]": "", "langDeAvailable": "", "langEnAvailable": "",
    "lang[]": "", "modStd[]": "", "cit[]": "", "tyi[]": "", "ins[]": "", "fee": "", "bgn[]": "",
    "dat[]": "", "prep_subj[]": "", "prep_degree[]": "", "sort": "4", "dur": "", "subjects[]": "",
    "q": "", "limit": "10000", "offset": "", "display": "list",
    "lvlDe[]": "", "lvlEn[]": ""
}

# Time (in seconds) to wait after loading the search page with Selenium
SELENIUM_WAIT = 5

# Timeout for individual detail page requests (in seconds)
REQUEST_TIMEOUT = 15