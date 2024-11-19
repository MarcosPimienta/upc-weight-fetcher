import requests
import json

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

def fetch_weight_from_upcitemdb_search(query, api_key):
    """
    Searches for a product using UPCItemDB API based on a search query.

    Parameters:
    - query: The search query constructed from product attributes.
    - api_key: The API key for authentication.

    Returns:
    - A tuple (upc, weight, unit) if successful, otherwise (None, None, None).
    """
    url = "https://api.upcitemdb.com/prod/trial/search"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'user_key': api_key,
        'key_type': '3scale'
    }
    params = {
        's': query
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            first_item = data['items'][0]  # Take the first item
            upc = first_item.get('upc', None)
            weight = first_item.get('weight', None)
            # Assuming the weight unit is included in the weight field, e.g., "1.2 pounds"
            if weight:
                weight_parts = weight.split()
                if len(weight_parts) == 2:
                    weight_value = float(weight_parts[0])
                    weight_unit = weight_parts[1]
                else:
                    weight_value = None
                    weight_unit = None
            else:
                weight_value = None
                weight_unit = None
            return upc, weight_value, weight_unit
        else:
            print(f"No data found for query '{query}'")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from UPCItemDB API for query '{query}': {e}")
        return None, None, None

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


def fetch_weight_from_red_circle(title, api_key):
    """
    Fetches the weight information for a given product title from the RedCircle API.

    Parameters:
    - title: The product title to search for.
    - api_key: The API key for authentication.

    Returns:
    - A tuple (weight, unit) if successful, otherwise (None, None).
    """
    url = "https://api.redcircleapi.com/request"
    params = {
        'api_key': api_key,
        'search_term': title,
        'category_id': '5zja3',  # Example category; update as needed
        'type': 'search'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Example parsing logic; adjust based on the actual API response
        if 'items' in data and len(data['items']) > 0:
            first_item = data['items'][0]  # Assume we use the first search result
            weight = first_item.get('weight')
            unit = first_item.get('unit')
            return weight, unit
        else:
            print(f"No weight data found for title '{title}'")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RedCircle API for title '{title}': {e}")
        return None, None

def fetch_weights(upc_list, api_key):
    base_url = 'https://go-upc.com/api/v1/code/'
    headers = {'Authorization': f"Bearer {api_key}"}
    weight_data = []

    for upc in upc_list:
        response = requests.get(f"{base_url}{upc}", headers=headers)
        if response.status_code == 200:
            product_data = response.json()
            weight = product_data.get('weight')
            unit = product_data.get('unit', 'g')  # Default to grams if not specified
            if weight:
                weight_data.append((upc, weight, unit))
        else:
            print(f"Failed to fetch data for UPC {upc}: {response.status_code}")

    return weight_data

def fetch_weight_from_go_upc(upc, api_key):
    """
    Fetches the weight information for a given UPC from the Go-UPC API.

    Parameters:
    - upc: The UPC code for the product.
    - api_key: The API key for authentication.

    Returns:
    - A tuple (weight, unit) if successful, otherwise (None, None).
    """
    url = f"https://api.go-upc.com/request/{upc}"
    headers = {'Authorization': f"Bearer {api_key}"}
    params = {
        'api_key': api_key
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Adjust this based on the actual API response structure
        weight = data.get('weight')
        unit = data.get('unit')
        return weight, unit
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for UPC {upc}: {e}")
        return None, None
