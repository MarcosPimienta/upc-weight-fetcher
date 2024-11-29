import requests
import time
from colorama import Fore, Style

def fetch_weights_from_red_circle(query, api_key, throttle_time, success_counter, failure_counter, query_type="search"):
    """
    Fetches product data using RedCircle API based on query type.

    Parameters:
    - query: The query term (e.g., Title, UPC, etc.).
    - api_key: The API key for authentication.
    - throttle_time: Time in seconds to wait between API requests.
    - success_counter: A list to track successful responses.
    - failure_counter: A list to track failed responses.
    - query_type: The type of query ('search', 'category', 'product').

    Returns:
    - A dictionary with extracted data if successful, otherwise None.
    """
    url = "https://api.redcircleapi.com/request"
    params = {
        "api_key": api_key,
        "type": query_type,
    }

    # Adjust parameters based on query type
    if query_type == "product":
        params["gtin"] = query  # Use GTIN for product type queries
    elif query_type == "category":
        params["category"] = query  # Use category name
    else:  # Default to 'search'
        params["search_term"] = query

    print(f"{Fore.YELLOW}Querying RedCircle for '{query}' (type: {query_type}){Style.RESET_ALL}")
    try:
        response = requests.get(url, params=params)
        print(f"{Fore.BLUE}Request URL:{Style.RESET_ALL} {response.url}")  # Debug URL
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400

        # Parse the response JSON
        data = response.json()
        if "product" in data:
            product = data["product"]
        elif "items" in data and data["items"]:
            product = data["items"][0]
        else:
            print(f"{Fore.RED}No results for query '{query}'{Style.RESET_ALL}")
            failure_counter.append(1)
            return None

        # Extract relevant details
        success_counter.append(1)
        return {
            "title": product.get("title", "N/A"),
            "upc": product.get("upc", "N/A"),
            "brand": product.get("brand", "N/A"),
            "category": product.get("breadcrumbs", [{}])[-1].get("name", "N/A"),
            "description": product.get("description", "N/A"),
            "price": product.get("buybox_winner", {}).get("price", {}).get("value", "N/A"),
            "currency": product.get("buybox_winner", {}).get("price", {}).get("currency", "N/A"),
            "weight": product.get("weight", "N/A"),
            "dimensions": product.get("dimensions", "N/A"),
            "main_image": product.get("main_image", {}).get("link", "N/A"),
        }

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching data from RedCircle API for query '{query}': {e}{Style.RESET_ALL}")
        failure_counter.append(1)
        return None
    finally:
        time.sleep(throttle_time)
