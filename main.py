import sys
import pandas as pd
from modules.data_fetcher import fetch_weight_from_go_upc, fetch_weight_from_red_circle
from modules.file_handler import load_excel, save_to_excel, save_to_csv

def main():
    if len(sys.argv) < 4:
        print("Usage: python main.py <path_to_excel_file> <api_key> <api_choice>")
        print("api_choice: 'red' for RedCircle API, 'go-upc' for Go-UPC API")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = sys.argv[2]
    api_choice = sys.argv[3].lower()

    if api_choice not in ['red', 'go-upc']:
        print("Invalid api_choice. Use 'red' for RedCircle API or 'go-upc' for Go-UPC API.")
        sys.exit(1)

    # Load data from the first sheet, assuming correct header row
    df = load_excel(file_path, sheet_name=0, header_row=0)

    # Drop any fully empty rows or columns
    df.dropna(how="all", inplace=True)
    df.columns = df.columns.str.strip()  # Strip whitespace from all column names

    # Print all columns to debug and identify exact column names
    print("Column names in the loaded DataFrame:", df.columns.tolist())

    # Check necessary columns
    required_columns = ['upc', 'title', 'description', 'weight', 'images']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found in the data.")
            sys.exit(1)

    # Ensure 'upc' column is treated as a string and fill NaN with "N/A"
    df['upc'] = df['upc'].astype(str).fillna("N/A")

    # Prepare a list to store processed data
    processed_data = []

    # Process each product row
    for _, row in df.iterrows():
        upc = row['upc'].strip()
        title = row.get('title', 'N/A')
        description = row.get('description', 'N/A')
        weight = row.get('weight', 'Unknown')
        images = row.get('images', 'N/A')

        # Fetch updated weight data if weight is missing or marked as "Unknown"
        if weight == "Unknown":
            if api_choice == 'go-upc':
                weight_data = fetch_weight_from_go_upc(upc, api_key)
            elif api_choice == 'red':
                weight_data = fetch_weight_from_red_circle(title, api_key)
            else:
                weight_data = None

            if weight_data:
                fetched_weight, unit = weight_data
                weight = fetched_weight if not unit else f"{fetched_weight} {unit}"

        # Add to processed data
        processed_data.append({
            'upc': upc,
            'title': title,
            'description': description,
            'weight': weight,
            'images': images
        })

    # Create DataFrame from processed data
    output_df = pd.DataFrame(processed_data)

    # Save to new CSV and Excel files
    save_to_csv(output_df, "updated_products.csv")
    save_to_excel(output_df, "updated_products.xlsx")

    print(f"Files 'updated_products.csv' and 'updated_products.xlsx' generated successfully using the {api_choice} approach.")

if __name__ == "__main__":
    main()
