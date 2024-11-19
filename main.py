import sys
import pandas as pd
import inquirer
from modules.data_fetcher import fetch_weight_from_go_upc, fetch_weight_from_red_circle
from modules.file_handler import load_excel, save_to_excel, save_to_csv

def main():
    # Step 1: Ask for file path, API key, and API choice
    questions = [
        inquirer.Text('file_path', message="Enter the path to your Excel file"),
        inquirer.Text('api_key', message="Enter your API key"),
        inquirer.List(
            'api_choice',
            message="Choose the API to use",
            choices=['red (RedCircle API)', 'go-upc (Go-UPC API)'],
            default='red (RedCircle API)'
        ),
    ]
    answers = inquirer.prompt(questions)
    file_path = answers['file_path']
    api_key = answers['api_key']
    api_choice = 'red' if 'red' in answers['api_choice'].lower() else 'go-upc'

    # Step 2: Load the Excel file and display columns
    try:
        df = load_excel(file_path, sheet_name=0, header_row=0)
        df.dropna(how="all", inplace=True)  # Drop empty rows
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

    """ print("\nAvailable columns in the file:")
    for idx, col in enumerate(df.columns.tolist(), start=1):
        print(f"{idx}. {col}") """

    # Step 3: Prompt user to select desired columns
    column_choices = inquirer.Checkbox(
        'columns',
        message="Select the columns you want to include in the output",
        choices=df.columns.tolist(),
    )
    selected_columns = inquirer.prompt([column_choices])['columns']

    if not selected_columns:
        print("No columns selected. Exiting.")
        sys.exit(1)

    # Step 4: Process selected columns
    processed_data = []
    for _, row in df.iterrows():
        processed_row = {}
        for col in selected_columns:
            value = row.get(col, 'N/A')

            # Special handling for 'weight' column
            if col == 'weight' and value == "Unknown":
                if api_choice == 'go-upc':
                    weight_data = fetch_weight_from_go_upc(row.get('upc', 'N/A'), api_key)
                elif api_choice == 'red':
                    weight_data = fetch_weight_from_red_circle(row.get('title', 'N/A'), api_key)
                else:
                    weight_data = None

                if weight_data:
                    fetched_weight, unit = weight_data
                    value = f"{fetched_weight} {unit}" if fetched_weight and unit else "N/A"

            processed_row[col] = value

        processed_data.append(processed_row)

    # Step 5: Save to new files
    output_df = pd.DataFrame(processed_data)
    save_to_csv(output_df, "updated_products.csv")
    save_to_excel(output_df, "updated_products.xlsx")

    print("\nFiles 'updated_products.csv' and 'updated_products.xlsx' generated successfully.")

if __name__ == "__main__":
    main()
