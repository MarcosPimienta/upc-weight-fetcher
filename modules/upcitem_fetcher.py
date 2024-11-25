import requests
import re
import time
from colorama import Fore, Style
from utils.data_converter import truncate_title

def fetch_weight_from_upcitemdb_search(product_name, api_key, throttle_time, success_counter, failure_counter, max_retries=3):
    """
    Searches for a product using UPCItemDB API with retry attempts and progressive truncation.

    Parameters:
    - product_name: The product name as a string.
    - api_key: The API key for authentication.
    - throttle_time: Time in seconds to wait between API requests.
    - success_counter: A list to track successful responses.
    - failure_counter: A list to track failed responses.
    - max_retries: The maximum number of retry attempts for a failed query.

    Returns:
    - A dictionary with extracted data (e.g., UPC, weight, brand, etc.) if successful, otherwise None.
    """
    original_name = product_name
    truncated_titles = truncate_title(product_name)  # Generate a list of truncated titles
    attempt = 0

    while attempt < max_retries and attempt < len(truncated_titles):
        product_name = truncated_titles[attempt]
        attempt += 1

        # Sanitize product name for URL
        sanitized_name = re.sub(r'[^a-zA-Z0-9\s/\-]', '', product_name)
        sanitized_name = re.sub(r'\s+', '%20', sanitized_name).strip()

        # Construct request URL
        url = f"https://api.upcitemdb.com/prod/v1/search?s={sanitized_name}&type=product&match_mode=1"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'user_key': api_key,
            'key_type': '3scale',
        }

        print(f"{Fore.YELLOW}Attempt {attempt}/{max_retries}: Querying '{product_name}'{Style.RESET_ALL}")
        try:
            response = requests.get(url, headers=headers)
            print(f"{Fore.BLUE}Request URL:{Style.RESET_ALL} {response.url}")

            if response.status_code == 429:  # Rate limit exceeded
                print(f"{Fore.YELLOW}Rate limit exceeded. Waiting for reset...{Style.RESET_ALL}")
                reset_time = int(response.headers.get("x-ratelimit-reset", time.time() + 60))
                wait_time = max(0, reset_time - int(time.time()))
                time.sleep(wait_time + 1)
                continue

            response.raise_for_status()

            # Parse the response JSON
            data = response.json()
            if data.get("code") == "OK" and data.get("items"):
                print(f"{Fore.GREEN}Successfully fetched data for '{product_name}'{Style.RESET_ALL}")
                success_counter.append(1)
                first_item = data['items'][0]
                return {
                    "upc": first_item.get("upc"),
                    "weight": first_item.get("weight"),
                    "brand": first_item.get("brand"),
                    "title": first_item.get("title"),
                    "description": first_item.get("description"),
                    "category": first_item.get("category"),
                    "images": first_item.get("images"),
                    "risky": "Yes" if attempt > 1 else "No",
                }

            print(f"{Fore.RED}No results for product name '{product_name}'{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error fetching data from UPCItemDB API for product '{product_name}': {e}{Style.RESET_ALL}")
        finally:
            time.sleep(throttle_time)

    print(f"{Fore.RED}Failed to fetch data for product '{original_name}' after {attempt} attempts.{Style.RESET_ALL}")
    failure_counter.append(1)
    return None
