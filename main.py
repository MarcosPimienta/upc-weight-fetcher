import sys
import pandas as pd
import inquirer
from modules.data_fetcher import (
    fetch_weight_from_upcitemdb_search,
    fetch_weight_from_go_upc,
    fetch_weight_from_red_circle,
    test_api_connection
)
from modules.data_converter import convert_to_grams
from modules.file_handler import load_excel, save_to_excel, save_to_csv

def main():
    # Step 1: Ask for file path, API key, and API choice
    questions = [
        inquirer.Text('file_path', message="Enter the path to your Excel file"),
        inquirer.Text('api_key', message="Enter your API key"),
        inquirer.List(
            'api_choice',
            message="Choose the API to use",
            choices=[
                'upcitemdb (UPCItemDB API)',
                'red (RedCircle API)',
                'go-upc (Go-UPC API)'
            ],
            default='upcitemdb (UPCItemDB API)'
        ),
    ]
    answers = inquirer.prompt(questions)
    file_path = answers['file_path']
    api_key = answers['api_key']
    api_choice = (
        'upcitemdb' if 'upcitemdb' in answers['api_choice'].lower()
        else 'red' if 'red' in answers['api_choice'].lower()
        else 'go-upc'
    )

    # Step 2: Test API connectivity
    print("\nTesting API connection...")
    if not test_api_connection(api_choice, api_key):
        print("Failed to connect to the API. Please check your API key or network connection.")
        sys.exit(1)
    print("API connection successful!\n")

    # Step 3: Load the Excel file and display columns
    try:
        df = load_excel(file_path, sheet_name=0, header_row=0)
        df.dropna(how="all", inplace=True)  # Drop empty rows
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

    print("\nAvailable columns in the file:")
    for idx, col in enumerate(df.columns.tolist(), start=1):
        print(f"{idx}. {col}")

    # Step 4: Prompt user to select columns for output
    column_choices = inquirer.Checkbox(
        'columns',
        message="Select the columns you want to include in the output",
        choices=df.columns.tolist(),
    )
    selected_columns = inquirer.prompt([column_choices])['columns']

    if not selected_columns:
        print("No columns selected. Exiting.")
        sys.exit(1)

    # Step 5: Prompt user to select columns for constructing search queries
    search_columns_choices = inquirer.Checkbox(
        'search_columns',
        message="Select the columns to use for searching UPCs (e.g., title, brand, model)",
        choices=df.columns.tolist(),
    )
    search_columns = inquirer.prompt([search_columns_choices])['search_columns']

    if not search_columns:
        print("No search columns selected. Exiting.")
        sys.exit(1)

    # Step 6: Process the data
    processed_data = []
    for _, row in df.iterrows():
        processed_row = {}
        search_terms = []

        # Construct search query from specified columns
        for col in search_columns:
            value = str(row.get(col, '')).strip()
            if value:
                search_terms.append(value)

        search_query = ' '.join(search_terms)

        # Fetch UPC and weight using the selected API
        if search_query:
            if api_choice == 'upcitemdb':
                upc, weight, unit = fetch_weight_from_upcitemdb_search(search_query, api_key)
            elif api_choice == 'red':
                upc, weight, unit = fetch_weight_from_red_circle(search_query, api_key)
            elif api_choice == 'go-upc':
                upc, weight, unit = fetch_weight_from_go_upc(search_query, api_key)
            else:
                upc, weight, unit = None, None, None

            # Update UPC
            if upc:
                processed_row['upc'] = upc
            else:
                processed_row['upc'] = 'N/A'

            # Convert weight to grams if available
            if weight and unit:
                weight_in_grams = convert_to_grams(weight, unit)
                processed_row['weight'] = weight_in_grams
            else:
                processed_row['weight'] = 'N/A'
        else:
            processed_row['upc'] = 'N/A'
            processed_row['weight'] = 'N/A'

        # Include other selected columns
        for col in selected_columns:
            if col not in ['upc', 'weight']:
                processed_row[col] = row.get(col, 'N/A')

        processed_data.append(processed_row)

    # Step 7: Save to new files
    output_df = pd.DataFrame(processed_data)
    save_to_csv(output_df, "updated_products.csv")
    save_to_excel(output_df, "updated_products.xlsx")

    print("\nFiles 'updated_products.csv' and 'updated_products.xlsx' generated successfully.")

if __name__ == "__main__":
    main()
