import sys
import pandas as pd
from modules.data_fetcher import fetch_weight_from_go_upc
from modules.data_converter import convert_to_grams
from modules.file_handler import load_excel, save_to_excel, save_to_csv

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <path_to_excel_file> <api_key>")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = sys.argv[2]

    # Load data from the second sheet, specifying the correct header row
    df = load_excel(file_path, sheet_name=0, header_row=0)

    # Drop any fully empty rows or columns
    df.dropna(how="all", inplace=True)
    df.columns = df.columns.str.strip()  # Strip whitespace from all column names

    # Print all columns to debug and identify exact column names
    print("Column names in the loaded DataFrame:", df.columns.tolist())

    # Check necessary columns (Remove 'Handle' and 'Option1 Name' as they are not needed for Go-UPC API)
    required_columns = ['Variant SKU', 'UPC', 'Title', 'Variant Grams']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found in the data.")
            sys.exit(1)

    # Ensure 'UPC' column is treated as a string and fill NaN with "N/A"
    df['UPC'] = df['UPC'].astype(str).fillna("N/A")

    # Ensure 'Variant Grams' column is treated as a string and fill NaN with "Unknown"
    df['Variant Grams'] = df['Variant Grams'].astype(str).fillna("Unknown")

    # Iterate through each row to fetch and update weights
    for index, row in df.iterrows():
        upc = row['UPC'].strip()

        # If UPC is valid, fetch weight from Go-UPC API
        if upc != "N/A" and upc != "Unknown":
            weight_data = fetch_weight_from_go_upc(upc, api_key)  # Go-UPC API function
            if weight_data:
                fetched_weight, unit = weight_data
                weight_in_grams = convert_to_grams(fetched_weight, unit) if fetched_weight and unit else "N/A"
                df.at[index, 'Variant Grams'] = weight_in_grams
            else:
                df.at[index, 'Variant Grams'] = "N/A"

    # Save updated DataFrame to new CSV and Excel files
    save_to_csv(df, "go-upc-products.csv")
    save_to_excel(df, "go-upc-products.xlsx")

    print("Files 'go-upc-products.csv' and 'go-upc-products.xlsx' generated successfully.")

if __name__ == "__main__":
    main()
