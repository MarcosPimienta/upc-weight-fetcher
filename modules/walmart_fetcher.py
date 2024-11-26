import requests
import time
from colorama import Fore, Style

def fetch_product_from_walmart(upc, auth_token, throttle_time):
    """
    Fetches product details from Walmart Product Lookup API.

    Parameters:
    - upc: The product UPC as a string.
    - auth_token: The generated Walmart API authentication token.
    - throttle_time: Time in seconds to wait between API requests.

    Returns:
    - A dictionary with product details if successful, otherwise None.
    """
    url = f"https://developer.api.walmart.com/v3/items?upc={upc}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }

    try:
        print(f"{Fore.YELLOW}Querying Walmart API for UPC: {upc}{Style.RESET_ALL}")
        response = requests.get(url, headers=headers)
        print(f"{Fore.BLUE}Request URL: {response.url}{Style.RESET_ALL}")

        if response.status_code == 429:
            print(f"{Fore.YELLOW}Rate limit exceeded. Waiting for reset...{Style.RESET_ALL}")
            time.sleep(throttle_time + 1)
            return None

        response.raise_for_status()

        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            print(f"{Fore.GREEN}Successfully fetched data for UPC: {upc}{Style.RESET_ALL}")
            first_item = data["items"][0]
            return {
                "title": first_item.get("name", "N/A"),
                "upc": upc,
                "brand": first_item.get("brand", "N/A"),
                "price": first_item.get("price", "N/A"),
                "description": first_item.get("description", "N/A"),
                "images": first_item.get("images", []),
                "category": first_item.get("categoryPath", "N/A"),
            }
        else:
            print(f"{Fore.RED}No results for UPC: {upc}{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching data from Walmart API for UPC {upc}: {e}{Style.RESET_ALL}")
        return None
    finally:
        time.sleep(throttle_time)
