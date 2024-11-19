import requests
import json

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
