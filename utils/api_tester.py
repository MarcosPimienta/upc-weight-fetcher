import requests

def test_api_connection(api_choice, api_key):
    """
    Tests the API connection for the selected API.

    Parameters:
    - api_choice: The selected API name (e.g., "UPCItemDB", "RedCircle", "Go-UPC", "Walmart").
    - api_key: The API key for authentication.

    Returns:
    - True if the connection is successful, False otherwise.
    """
    url = None
    headers = None
    params = None

    if api_choice == "UPCItemDB":
        url = "https://api.upcitemdb.com/prod/v1/lookup?upc=4002293401102"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "user_key": api_key,
        }
    elif api_choice == "RedCircle":
        url = "https://api.redcircleapi.com/request"
        params = {"api_key": api_key, "search_term": "test", "type": "search"}
    elif api_choice == "Go-UPC":
        url = "https://api.go-upc.com/request/test"
        headers = {"Authorization": f"Bearer {api_key}"}
    elif api_choice == "Walmart":
        url = "https://developer.api.walmart.com/v3/items?upc=4002293401102"
        headers = {"Authorization": f"Bearer {api_key}"}
    else:
        return False

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"API connection test failed: {e}")
        return False