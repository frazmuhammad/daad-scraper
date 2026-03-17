# excel_exporter.py
"""
Reads the scraped data from the database and writes it to an Excel file.
"""

import sqlite3
import pandas as pd
from config import SCRAPER_DB

def export_to_excel(output_file, db_path=SCRAPER_DB):
    """
    Fetch all courses from the database and save them to an Excel file.
    Adds a serial number column and renames columns for readability.
    """
    print(f"📊 Generating Excel file: {output_file}...")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM courses", conn)
    conn.close()

    if df.empty:
        print("⚠️ No data in database to export.")
        return

    # Add serial number column at the beginning
    df.insert(0, 'S.No', range(1, len(df) + 1))

    # Reorder columns (optional, but keeps a consistent order)
    column_order = ["S.No", "course_name", "university", "city", "admission_req", "language_req", "deadline", "url"]
    df = df[column_order]

    # Rename columns for the final Excel
    df.columns = ["S.No", "Course Name", "University", "City", "Admission Req", "Language Req", "Deadline", "URL"]

    df.to_excel(output_file, index=False)
    print(f"✅ Excel saved with {len(df)} rows.")