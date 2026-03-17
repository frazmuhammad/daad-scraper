# DAAD Study Programme Scraper

A modular Python tool to interactively build search filters, scrape course details from the DAAD International Programmes database, and export the results to an Excel file.

## Features
* **Interactive Filter Selection:** Choose degree type, subject groups, language, fees, semester, and more.
* **Automatic URL Construction:** Uses `limit=10000` to attempt to retrieve all results on a single page.
* **Multi-threaded Scraping:** Faster extraction of course detail pages.
* **Persistent Storage:** Uses SQLite to resume scraping where it left off.
* **Excel Export:** Saves data into a clean, formatted `.xlsx` file.

## Requirements
* Python 3.7+
* Google Chrome Browser (for Selenium)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/daad-scraper.git](https://github.com/your-username/daad-scraper.git)
    cd daad-scraper
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Filters Database
The scraper requires a SQLite database (`daad_filters.db`) containing filter definitions and option codes.

* **If you have the database file:** Place it in the root folder of the project.
* **If you need to create it:** Run the provided setup script:
    ```bash
    python create_daad_db.py
    ```
    This generates `daad_filters.db` with the currently known filter parameters.

## Usage
Run the main script to start the interactive session:

```bash
python main.py
```

## Workflow:
* **Select Filters:** Follow the interactive prompts to choose specific search parameters (e.g., "Master's degree").
* **Output Name:** Provide a name for the output Excel file (default: DAAD_Results.xlsx).
* **Scraping:** The script builds the search URL, identifies new courses, and scrapes details using multi-threading.
* **Storage:** Data is saved to daad_data2.db and then exported to Excel.

## Configuration

Modify `config.py` to adjust the scraper behavior:

| Variable | Description |
| :--- | :--- |
| **FILTERS_DB** | Path to the filter definitions database. |
| **SCRAPER_DB** | Path to the course data database. |
| **MAX_WORKERS** | Number of concurrent threads for scraping. |
| **REQUEST_TIMEOUT** | Timeout for HTTP requests (seconds). |
| **SELENIUM_WAIT** | Wait time for search page elements to load. |
| **DEFAULT_PARAMS** | Default URL query parameters (e.g., `limit=10000`). |

## File Structure

```text
daad_scraper/
├── config.py           # Central configuration
├── filters_db.py       # Loads filter definitions
├── url_builder.py      # Builds DAAD URLs & interactive menus
├── scraper.py          # Scraping logic (Selenium + Requests)
├── excel_exporter.py   # Exports database to Excel
├── main.py             # Main entry point
├── daad_filters.db     # Database file with filter values
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
