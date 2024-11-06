import sys
import pandas as pd
from modules.data_fetcher import fetch_weights
from modules.data_converter import convert_to_grams
from modules.file_handler import load_excel, save_to_excel, save_to_csv

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <path_to_excel_file> <api_key>")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = sys.argv[2]

    # Load data from the second sheet with specified header row
    df = load_excel(file_path, sheet_name=1, header_row=1)

    # Debug: print column names to ensure we have the correct ones
    print("Column names in the loaded DataFrame:", df.columns)

    # Check if 'Weight' and 'UPC/EAN' columns exist
    if 'Weight' not in df.columns or 'UPC/EAN' not in df.columns:
        print("Error: Required columns ('Weight' or 'UPC/EAN') not found in the data.")
        sys.exit(1)

    # Filter UPCs with missing weights
    upc_list = df[df['Weight'].isna()]['UPC/EAN'].unique()

    # Fetch and convert weights for missing UPCs
    weights_data = fetch_weights(upc_list, api_key)
    weights_data = [(upc, convert_to_grams(weight, unit)) for upc, weight, unit in weights_data]

    # Update DataFrame with fetched weights
    weight_df = pd.DataFrame(weights_data, columns=['UPC/EAN', 'Weight'])
    df = df.merge(weight_df, on='UPC/EAN', how='left', suffixes=('', '_fetched'))
    df['Weight'] = df['Weight'].fillna(df['Weight_fetched'])
    df.drop(columns=['Weight_fetched'], inplace=True)

    # Save updated data to new files
    save_to_excel(df, "updated_products.xlsx")
    save_to_csv(df, "updated_products.csv")

if __name__ == "__main__":
    main()
