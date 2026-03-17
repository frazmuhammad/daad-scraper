# main.py
"""
Main entry point for the DAAD scraper.
Loads filters, lets the user select them interactively, builds the search URL,
asks for an output file name, and starts scraping.
"""

import config
from filters_db import load_filters_from_db
from url_builder import build_daad_url, select_filters_interactively
from scraper import run_scraper

def main():
    # 1. Load filter definitions from the filters database
    filters_dict = load_filters_from_db(config.FILTERS_DB)
    if not filters_dict:
        print(f"No filters loaded from filter database. Make sure '{config.FILTERS_DB}' exists and has data.")
        return

    # 2. Interactive filter selection
    selected = select_filters_interactively(filters_dict)

    # 3. Build the search URL
    if selected:
        print("\nSelected filters:")
        for k, v in selected.items():
            print(f"  {k}: {v}")
        search_url = build_daad_url(selected, filters_dict,
                                    base_url=config.BASE_URL,
                                    default_params=config.DEFAULT_PARAMS)
    else:
        print("No filters selected. Using default search (all programmes).")
        search_url = build_daad_url({}, filters_dict,
                                    base_url=config.BASE_URL,
                                    default_params=config.DEFAULT_PARAMS)

    print(f"\nGenerated Search URL:\n{search_url}")

    # 4. Ask for output Excel file name
    default_output = "DAAD_Results.xlsx"
    output_file = input(f"\nEnter output Excel file name (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    if not output_file.endswith('.xlsx'):
        output_file += '.xlsx'

    # 5. Run the scraper
    run_scraper(search_url, output_file,
                db_path=config.SCRAPER_DB,
                max_workers=config.MAX_WORKERS,
                headers=config.HEADERS)

if __name__ == "__main__":
    main()