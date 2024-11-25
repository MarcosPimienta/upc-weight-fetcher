import requests
import time
from colorama import Fore, Style

def fetch_weights_from_go_upc(upc, api_key, throttle_time):
    """
    Searches for a product using Go-UPC API based on a UPC.

    Parameters:
    - upc: The product UPC as a string.
    - api_key: The API key for authentication.
    - throttle_time: Time in seconds to wait between API requests.

    Returns:
    - A dictionary with extracted data (e.g., weight, unit) if successful, otherwise None.
    """
    url = f"https://go-upc.com/api/v1/lookup/{upc}"
    headers = {'Authorization': f"Bearer {api_key}"}

    print(f"{Fore.YELLOW}Querying Go-UPC for UPC '{upc}'{Style.RESET_ALL}")
    try:
        response = requests.get(url, headers=headers)
        print(f"{Fore.BLUE}Request URL:{Style.RESET_ALL} {response.url}")
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()
        if not data.get("item"):
            print(f"{Fore.RED}No results for UPC '{upc}'{Style.RESET_ALL}")
            return None

        item = data['item']
        return {
            "weight": item.get("weight"),
            "unit": item.get("unit"),
        }

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching data from Go-UPC API for UPC '{upc}': {e}{Style.RESET_ALL}")
        return None
    finally:
        time.sleep(throttle_time)