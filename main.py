import sys
import pandas as pd
from modules.data_fetcher import fetch_weights_from_red_circle
from modules.data_converter import convert_to_grams
from modules.file_handler import load_excel, save_to_excel, save_to_csv

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <path_to_excel_file> <api_key>")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = sys.argv[2]

    # Load data from the second sheet, specifying the correct header row
    df = load_excel(file_path, sheet_name=1, header_row=0)

    # Drop any fully empty rows or columns
    df.dropna(how="all", inplace=True)
    df.columns = df.columns.str.strip()  # Strip whitespace from all column names

    # Print all columns to debug and identify exact column names
    print("Column names in the loaded DataFrame:", df.columns.tolist())

    # Check necessary columns
    required_columns = ['Variant SKU', 'UPC', 'Title', 'Variant Grams', 'Handle', 'Option1 Name']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found in the data.")
            sys.exit(1)

    # Ensure 'UPC' column is treated as a string and fill NaN with "N/A"
    df['UPC'] = df['UPC'].astype(str).fillna("N/A")

    # Ensure 'Variant Grams' column is treated as a string and fill NaN with "Unknown"
    df['Variant Grams'] = df['Variant Grams'].astype(str).fillna("Unknown")

    # Prepare a list to store processed data
    processed_data = []

    # Process each product row
    for _, row in df.iterrows():
        sku = row['Variant SKU']
        upc = row['UPC'].strip()  # Now 'UPC' is guaranteed to be a string
        title = row.get('Title', 'N/A')
        handle = row.get('Handle', 'N/A')
        option1_name = row.get('Option1 Name', 'N/A')
        weight = row['Variant Grams'].strip()  # Now 'Variant Grams' is guaranteed to be a string

        # If UPC is missing or marked as "Unknown"
        if not upc or upc == "Unknown":
            # Fetch weight using Red Circle API based on Title, Handle, or Option1 Name
            weight_data = fetch_weights_from_red_circle(handle, title, option1_name, api_key)
            if weight_data:
                fetched_weight, unit = weight_data
                weight = convert_to_grams(fetched_weight, unit) if fetched_weight and unit else "N/A"
            else:
                weight = "N/A"

        # Add to processed data
        processed_data.append({
            'Title': title,
            'SKU': sku,
            'UPC': upc if upc else "N/A",
            'Weight': weight
        })

    # Create DataFrame from processed data
    output_df = pd.DataFrame(processed_data)

    # Save to new CSV and Excel files
    save_to_csv(output_df, "processed_products.csv")
    save_to_excel(output_df, "processed_products.xlsx")

if __name__ == "__main__":
    main()
