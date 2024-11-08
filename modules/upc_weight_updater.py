import pandas as pd
import requests

def fetch_weight_from_go_upc(upc, api_key):
    """Fetches the weight information for a given UPC from the Go-UPC API."""
    url = f"https://api.go-upc.com/request/{upc}"
    headers = {'Authorization': f"Bearer {api_key}"}
    params = {
        'api_key': api_key
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # Adjust this according to the actual structure of the API response
        weight = data.get('weight')
        unit = data.get('unit')
        return weight, unit
    else:
        print(f"Failed to fetch data for UPC {upc}: {response.status_code}")
        return None, None

def update_variant_grams(file_path, api_key):
    """Updates the Variant Grams column with weight information from the Go-UPC API."""
    # Load the Excel file
    df = pd.read_excel(file_path, sheet_name=0)

    # Check for required columns
    if 'UPC' not in df.columns or 'Variant Grams' not in df.columns:
        print("Error: Required columns 'UPC' and 'Variant Grams' not found in the data.")
        return

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        upc = row['UPC']

        # Skip rows where UPC is missing or marked as "Unknown"
        if pd.isna(upc) or upc == "Unknown":
            df.at[index, 'Variant Grams'] = "N/A"
            continue

        # Fetch weight information from Go-UPC API
        weight, unit = fetch_weight_from_go_upc(upc, api_key)

        # Convert weight to grams if needed and update the 'Variant Grams' column
        if weight and unit:
            if unit.lower() == 'kg':
                weight = weight * 1000  # Convert kg to grams
            elif unit.lower() == 'lb':
                weight = weight * 453.592  # Convert pounds to grams
            elif unit.lower() == 'oz':
                weight = weight * 28.3495  # Convert ounces to grams

            df.at[index, 'Variant Grams'] = weight
        else:
            df.at[index, 'Variant Grams'] = "N/A"

    # Save the updated DataFrame to a new Excel file
    output_file = "updated_" + file_path
    df.to_excel(output_file, index=False)
    print(f"Updated file saved as {output_file}")

# Example usage:
# update_variant_grams("path/to/your/file.xlsx", "your_go_upc_api_key")
