import requests
import time
from colorama import Fore, Style

def fetch_weights_from_red_circle(query, api_key, throttle_time, success_counter, failure_counter):
    """
    Searches for a product using RedCircle API based on a query.

    Parameters:
    - query: The product query as a string.
    - api_key: The API key for authentication.
    - throttle_time: Time in seconds to wait between API requests.
    - success_counter: A list to track successful responses.
    - failure_counter: A list to track failed responses.

    Returns:
    - A dictionary with extracted data (e.g., weight, unit) if successful, otherwise None.
    """
    url = "https://api.redcircleapi.com/request"
    params = {
        'api_key': api_key,
        'search_term': query,
        'type': 'search',
    }

    print(f"{Fore.YELLOW}Querying RedCircle for '{query}'{Style.RESET_ALL}")
    try:
        response = requests.get(url, params=params)
        print(f"{Fore.BLUE}Request URL:{Style.RESET_ALL} {response.url}")  # Debug URL
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400

        # Parse the response JSON
        data = response.json()
        if not data.get("items"):
            print(f"{Fore.RED}No results for query '{query}'{Style.RESET_ALL}")
            failure_counter.append(1)
            return None

        # Extract the first item's details
        first_item = data['items'][0]
        success_counter.append(1)
        return {
            "weight": first_item.get("weight"),
            "unit": first_item.get("unit"),
        }

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching data from RedCircle API for query '{query}': {e}{Style.RESET_ALL}")
        failure_counter.append(1)
        return None
    finally:
        time.sleep(throttle_time)  # Wait for the specified throttle time
