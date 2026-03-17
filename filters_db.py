# filters_db.py
"""
Handles loading filter definitions and options from the filters database.
"""

import sqlite3
from config import FILTERS_DB

class Filter:
    """Represents a search filter with its options loaded from the database."""
    def __init__(self, display_name, url_param, is_multi):
        self.display_name = display_name
        self.url_param = url_param
        self.is_multi = bool(is_multi)
        self.options = {}  # option_name -> option_value

def load_filters_from_db(db_path=FILTERS_DB):
    """
    Load all filters and their options from the SQLite database.

    Args:
        db_path (str): Path to the filters database file.

    Returns:
        dict: Mapping from filter display name to Filter object.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load filters
    cursor.execute("SELECT id, display_name, url_param, is_multi FROM filters")
    filters = {}
    for row in cursor.fetchall():
        fid, display_name, url_param, is_multi = row
        f = Filter(display_name, url_param, is_multi)
        filters[display_name] = f

    # Load options for each filter
    cursor.execute("""
        SELECT f.display_name, fo.option_name, fo.option_value
        FROM filter_options fo
        JOIN filters f ON fo.filter_id = f.id
    """)
    for display_name, opt_name, opt_value in cursor.fetchall():
        if display_name in filters:
            filters[display_name].options[opt_name] = opt_value

    conn.close()
    return filters