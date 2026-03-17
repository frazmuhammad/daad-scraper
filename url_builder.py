# url_builder.py
"""
Builds DAAD search URLs from human‑readable filter selections.
Also provides an interactive menu for the user to choose filters.
"""

import urllib.parse
from config import BASE_URL, DEFAULT_PARAMS

def build_daad_url(selected_filters, filters_dict, base_url=BASE_URL, default_params=None):
    """
    Build a DAAD search URL from human-readable filter selections.

    Args:
        selected_filters (dict): Keys are filter display names, values are
                                 the selected human-readable option(s) (string or list).
        filters_dict (dict): The dictionary of Filter objects (from filters_db).
        base_url (str): The base search URL.
        default_params (dict): Default query parameters.

    Returns:
        str: Full DAAD search URL with encoded query string.
    """
    if default_params is None:
        default_params = DEFAULT_PARAMS.copy()
    params = default_params.copy()

    for display_name, human_value in selected_filters.items():
        if display_name not in filters_dict:
            print(f"Warning: Unknown filter '{display_name}' ignored.")
            continue
        f = filters_dict[display_name]
        url_param = f.url_param

        # Convert human value(s) to URL code(s)
        if isinstance(human_value, list):
            codes = []
            for val in human_value:
                code = f.options.get(val)
                if code:
                    codes.append(code)
                else:
                    codes.append(val)  # fallback (should not happen)
            params[url_param] = codes if len(codes) > 1 else (codes[0] if codes else "")
        else:
            code = f.options.get(human_value, human_value)
            params[url_param] = code

    # Remove empty parameters and build query string
    query_parts = []
    for key, value in params.items():
        if value == "" or value is None:
            continue
        if isinstance(value, list):
            for v in value:
                if v:
                    query_parts.append((key, v))
        else:
            query_parts.append((key, value))

    query_string = urllib.parse.urlencode(query_parts, doseq=True)
    return f"{base_url}?{query_string}"


def select_filters_interactively(filters_dict):
    """
    Interactively ask the user which filters to apply.

    Args:
        filters_dict (dict): The dictionary of Filter objects (from filters_db).

    Returns:
        dict: Selected human-readable option(s) for each chosen filter.
    """
    selected = {}

    print("DAAD Study Programme Search - Filter Selection")
    print("=" * 60)

    # List only filters that have options defined
    available_filters = [f for f in filters_dict.values() if f.options]

    for f in available_filters:
        print(f"\nFilter: {f.display_name}")
        print(f"URL parameter: {f.url_param} (multiple selections allowed: {'Yes' if f.is_multi else 'No'})")
        choice = input("Apply this filter? (y/n): ").strip().lower()
        if choice == 'y':
            option_list = list(f.options.keys())
            print("Available options:")
            for idx, opt in enumerate(option_list, 1):
                print(f"  {idx}. {opt}")

            if f.is_multi:
                selections = input("Enter numbers (comma-separated): ").strip()
                if selections:
                    indices = [int(i.strip()) for i in selections.split(',') if i.strip().isdigit()]
                    selected_opts = [option_list[i-1] for i in indices if 1 <= i <= len(option_list)]
                    if selected_opts:
                        selected[f.display_name] = selected_opts if len(selected_opts) > 1 else selected_opts[0]
                    else:
                        print("No valid options selected, skipping filter.")
                else:
                    print("No selection made, skipping filter.")
            else:
                idx = input("Enter number: ").strip()
                if idx.isdigit():
                    i = int(idx)
                    if 1 <= i <= len(option_list):
                        selected[f.display_name] = option_list[i-1]
                    else:
                        print("Invalid number, skipping filter.")
                else:
                    print("Invalid input, skipping filter.")
    return selected