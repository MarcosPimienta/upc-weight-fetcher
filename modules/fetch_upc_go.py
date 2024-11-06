import pandas as pd
import requests

API_KEY = 'your_api_key_here'
BASE_URL = 'https://go-upc.com/api/v1/code/'

# Function to fetch product data using UPC
def fetch_product_data(upc):
    url = f"{BASE_URL}{upc}"
    headers = {'Authorization': f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for UPC {upc}: {response.status_code}")
        return None

def convert_to_grams(weight, unit):
    conversion_factors = {
        'kg': 1000,
        'g': 1,
        'lb': 453.592,
        'oz': 28.3495
    }
    return weight * conversion_factors.get(unit.lower(), 1)

# Load the Excel sheet
file_path = 'path/to/your/excel_file.xlsx'
df = pd.read_excel(file_path)

# Filter for rows with missing weights and extract UPCs
upc_list = df[df['Weight'].isna()]['UPC/EAN'].unique()

# List to store results
data_with_weights = []

# Pull data for each UPC and convert weight if necessary
for upc in upc_list:
    product_data = fetch_product_data(upc)
    if product_data:
        weight = product_data.get('weight', None)
        unit = product_data.get('unit', 'g')  # Assuming 'g' as default if not provided
        if weight:
            weight_in_grams = convert_to_grams(weight, unit)
            data_with_weights.append({
                'UPC/EAN': upc,
                'Weight': weight_in_grams
            })

# Merge fetched weights back into the original DataFrame
weight_df = pd.DataFrame(data_with_weights)
df = df.merge(weight_df, on='UPC/EAN', how='left', suffixes=('', '_fetched'))
df['Weight'] = df['Weight'].fillna(df['Weight_fetched'])
df.drop(columns=['Weight_fetched'], inplace=True)

# Save as CSV and Excel
df.to_csv('updated_products.csv', index=False)
df.to_excel('updated_products.xlsx', index=False)
