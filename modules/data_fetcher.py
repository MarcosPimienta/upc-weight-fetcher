import requests

def fetch_weights_from_red_circle(handle, title, option1_name, api_key):
    url = 'https://api.redcircleapi.com/request'
    headers = {'Authorization': f"Bearer {api_key}"}

    # Use Title as the main search term; fallback to handle or option1_name if title is missing
    search_term = title or handle or option1_name

    # Set up the request parameters
    params = {
        'api_key': api_key,
        'search_term': search_term,
        'category_id': '5zja3',  # Update category_id if needed
        'type': 'search'
    }

    # Make the HTTP GET request to the RedCircle API
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # Assuming the API response includes 'weight' and 'unit'
        # Adjust according to the actual API response structure
        weight = data.get('weight')
        unit = data.get('unit')
        return weight, unit
    else:
        print(f"Failed to fetch data for {search_term}: {response.status_code}")
        return None

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
