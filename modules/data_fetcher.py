import requests
import json
import re
import time
from colorama import Fore, Style

def test_api_connection(api_choice, api_key):
    """
    Tests the API connection to ensure the provided API key is valid.

    Parameters:
    - api_choice: The selected API ('red', 'go-upc', 'upcitemdb').
    - api_key: The API key to test.

    Returns:
    - True if the connection is successful, otherwise False.
    """
    if api_choice == 'red':
        url = "https://api.redcircleapi.com/request"
        params = {
            'api_key': api_key,
            'search_term': 'test',
            'type': 'search'
        }
    elif api_choice == 'go-upc':
        url = f"https://api.go-upc.com/request/test"
        headers = {'Authorization': f"Bearer {api_key}"}
        params = {
            'api_key': api_key
        }
    elif api_choice == 'upcitemdb':
        url = "https://api.upcitemdb.com/prod/v1/lookup?upc=4002293401102"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'user_key': api_key,
            'key_type': '3scale'
        }
        params = None
    else:
        return False

    try:
        response = requests.get(url, headers=headers if api_choice in ['go-upc', 'upcitemdb'] else None, params=params)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"API connection test failed: {e}")
        return False

def truncate_title(title):
    """
    Truncates the product title progressively based on delimiters like ':' and '-',
    and removes leading numbers or numerical phrases.

    Parameters:
    - title: The original product title.

    Returns:
    - A list of progressively truncated titles.
    """
    # Remove leading numbers or numerical phrases
    clean_title = re.sub(r'^\d+\s*[a-zA-Z]*\s*', '', title).strip()  # e.g., "2pk 50\"x63\" ..." -> "blackout ..."

    # Split the title by delimiters ':' and '-'
    delimiters = [':', '-']
    truncated_titles = [clean_title]
    for delimiter in delimiters:
        if delimiter in clean_title:
            # Create progressively truncated titles
            parts = clean_title.split(delimiter)
            for i in range(1, len(parts)):
                truncated_titles.append(delimiter.join(parts[:i]).strip())
    return truncated_titles

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
    original_name = product_name  # Keep the original name for logging
    truncated_titles = truncate_title(product_name)  # Generate a list of truncated titles
    attempt = 0

    while attempt < max_retries and attempt < len(truncated_titles):
        # Use the next truncated title for each attempt
        product_name = truncated_titles[attempt]
        attempt += 1

        # Sanitize product name for URL
        sanitized_name = re.sub(r'[^a-zA-Z0-9\s/\-]', '', product_name)  # Keep alphanumeric, spaces, '/', and '-'
        sanitized_name = re.sub(r'\s+', '%20', sanitized_name).strip()  # Replace spaces with '%20'

        # Manually construct the request URL
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
            print(f"{Fore.BLUE}Request URL:{Style.RESET_ALL} {response.url}")  # Debug URL

            if response.status_code == 429:  # Rate limit exceeded
                print(f"{Fore.YELLOW}Rate limit exceeded. Waiting for reset...{Style.RESET_ALL}")
                reset_time = int(response.headers.get("x-ratelimit-reset", time.time() + 60))
                wait_time = max(0, reset_time - int(time.time()))
                time.sleep(wait_time + 1)  # Wait until rate limit resets
                continue

            response.raise_for_status()  # Raise an error for other HTTP status codes >= 400

            # Parse the response JSON
            data = response.json()
            if data.get("code") == "OK" and data.get("items"):
                print(f"{Fore.GREEN}Successfully fetched data for '{product_name}'{Style.RESET_ALL}")
                success_counter.append(1)
                # Extract the first item's details
                first_item = data['items'][0]
                return {
                    "upc": first_item.get("upc"),
                    "weight": first_item.get("weight"),
                    "brand": first_item.get("brand"),
                    "title": first_item.get("title"),
                    "description": first_item.get("description"),
                    "category": first_item.get("category"),
                    "images": first_item.get("images"),
                }

            print(f"{Fore.RED}No results for product name '{product_name}'{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error fetching data from UPCItemDB API for product '{product_name}': {e}{Style.RESET_ALL}")
        finally:
            time.sleep(throttle_time)  # Wait for the specified throttle time

    print(f"{Fore.RED}Failed to fetch data for product '{original_name}' after {attempt} attempts.{Style.RESET_ALL}")
    failure_counter.append(1)
    return None

def fetch_weight_from_upcitemdb(upc, api_key):
    """
    Fetches product details, including weight, from UPCItemDB API.

    Parameters:
    - upc: The UPC code for the product.
    - api_key: The API key for authentication.

    Returns:
    - A tuple (weight, unit) if successful, otherwise (None, None).
    """
    url = f"https://api.upcitemdb.com/prod/v1/lookup?upc={upc}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'user_key': api_key,
        'key_type': '3scale'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            first_item = data['items'][0]  # Take the first item
            weight = first_item.get('weight')  # Adjust based on API response structure
            unit = 'grams'  # Assuming unit as grams for simplicity
            return weight, unit
        else:
            print(f"No data found for UPC {upc}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from UPCItemDB API for UPC {upc}: {e}")
        return None, None


def fetch_weights_from_red_circle(query, api_key, throttle_time):
    """
    Searches for a product using RedCircle API based on a query.

    Parameters:
    - query: The product query as a string.
    - api_key: The API key for authentication.
    - throttle_time: Time in seconds to wait between API requests.

    Returns:
    - A dictionary with extracted data (e.g., weight, unit) if successful, otherwise None.
    """
    url = "https://api.redcircleapi.com/request"
    params = {
        'api_key': api_key,
        'search_term': query,
        'type': 'search',
    }

    try:
        response = requests.get(url, params=params)
        print(f"Request URL: {response.url}")  # Debug URL
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400

        # Parse the response JSON
        data = response.json()
        if not data.get("items"):
            print(f"No results for query '{query}'")
            return None

        # Extract the first item's details
        first_item = data['items'][0]
        return {
            "weight": first_item.get("weight"),
            "unit": first_item.get("unit"),
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RedCircle API for query '{query}': {e}")
        return None
    finally:
        time.sleep(throttle_time)  # Wait for the specified throttle time


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
    headers = {
        'Authorization': f"Bearer {api_key}",
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"Request URL: {response.url}")  # Debug URL
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400

        # Parse the response JSON
        data = response.json()
        if not data.get("item"):
            print(f"No results for UPC '{upc}'")
            return None

        # Extract the item's details
        item = data['item']
        return {
            "weight": item.get("weight"),
            "unit": item.get("unit"),
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Go-UPC API for UPC '{upc}': {e}")
        return None
    finally:
        time.sleep(throttle_time)
