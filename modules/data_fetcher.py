import requests

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
