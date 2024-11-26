import sys
import pandas as pd
import inquirer
from modules.red_circle_fetcher import fetch_weights_from_red_circle
from modules.upcitem_fetcher import fetch_weight_from_upcitemdb_search
from modules.go_upc_fetcher import fetch_weights_from_go_upc
from utils.api_tester import test_api_connection
from utils.data_converter import convert_to_grams
from modules.file_handler import save_to_excel_with_highlighting, save_to_csv
from colorama import Fore, Style


def main():
    # Step 1: Ask for file path and API key
    questions = [
        inquirer.Text("file_path", message="Enter the path to your Excel file"),
        inquirer.Text("api_key", message="Enter your API key"),
    ]
    answers = inquirer.prompt(questions)
    file_path = answers["file_path"]
    api_key = answers["api_key"]

    # Step 2: Ask which API to use and throttle time
    api_question = [
        inquirer.List(
            "api_choice",
            message="Which API do you want to use?",
            choices=["UPCItemDB", "RedCircle", "Go-UPC"],
        ),
        inquirer.Text(
            "throttle_time",
            message="Enter the throttle time (in seconds) between requests (e.g., 1 for 1 second)",
            validate=lambda _, x: x.isdigit() and int(x) >= 0,
        ),
    ]
    api_answers = inquirer.prompt(api_question)
    api_choice = api_answers["api_choice"]
    throttle_time = int(api_answers["throttle_time"])  # Convert input to integer

    # Step 3: Test API Connection
    print(f"\nTesting connection for {api_choice} API...")
    if not test_api_connection(api_choice, api_key):
        print(f"{api_choice} API Connection Failed. Please check your API key or query.")
        sys.exit(1)
    print(f"{api_choice} API Connection Successful!\n")

    # Step 4: Load Excel file and list available sheets
    try:
        sheets = pd.ExcelFile(file_path).sheet_names
        sheet_question = [
            inquirer.List(
                "sheet_name",
                message="Select the sheet to work with",
                choices=sheets,
            )
        ]
        sheet_name = inquirer.prompt(sheet_question)["sheet_name"]
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        sys.exit(1)

    # Step 5: Load the selected sheet
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
        df.dropna(how="all", inplace=True)  # Drop empty rows
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
    except Exception as e:
        print(f"Error loading sheet '{sheet_name}': {e}")
        sys.exit(1)

    # Step 6: Prompt user to select columns for output
    field_choices = [
        "Product Title",
        "Description",
        "Price",
        "SKU",
        "Brand",
        "Category",
        "Main Image URL",
    ]
    column_question = inquirer.Checkbox(
        "fields",
        message="Select the fields you want to query:",
        choices=field_choices,
    )
    selected_fields = inquirer.prompt([column_question])["fields"]

    # Ensure at least one field is selected
    if not selected_fields:
        print("No fields selected. Exiting.")
        sys.exit(1)

    # Step 7: Process the data
    processed_data = []
    total_queries = len(df)
    for index, row in enumerate(df.iterrows(), start=1):
        title = row[1].get("Title", "").strip()

        # Display query progress
        print(f"{Fore.CYAN}Processing query {index}/{total_queries}: {title}{Style.RESET_ALL}")

        # Fetch product details based on the selected API
        product_details = None
        if api_choice == "UPCItemDB":
            product_details = fetch_weight_from_upcitemdb_search(
                title, api_key, throttle_time, [], []
            )
        elif api_choice == "RedCircle":
            product_details = fetch_weights_from_red_circle(
                title, api_key, throttle_time, [], []
            )
        elif api_choice == "Go-UPC":
            product_details = fetch_weights_from_go_upc(
                title, api_key, throttle_time
            )

        # Initialize row data with "N/A" for all selected fields
        row_data = {field: "N/A" for field in selected_fields}

        # Update row data with fetched product details
        if product_details:
            for field in selected_fields:
                # Map fields to product details keys
                field_map = {
                    "Product Title": "title",
                    "Description": "description",
                    "Price": "price",
                    "SKU": "sku",
                    "Brand": "brand",
                    "Category": "category",
                    "Main Image URL": "images",
                }
                mapped_key = field_map.get(field)
                if mapped_key:
                    value = product_details.get(mapped_key, "N/A")
                    if field == "Main Image URL" and isinstance(value, list):
                        value = ", ".join(value)  # Join image URLs into a string
                    row_data[field] = value

        row_data["Title"] = title
        processed_data.append(row_data)

    # Step 8: Highlight rows with all "N/A" fields
    df_processed = pd.DataFrame(processed_data)
    all_na_mask = df_processed[selected_fields].eq("N/A").all(axis=1)
    for i in df_processed[all_na_mask].index:
        df_processed.loc[i, :] = df_processed.loc[i, :].apply(
            lambda x: f"{Fore.RED}{x}{Style.RESET_ALL}"
        )

    # Step 9: Save to Excel with red highlighting for rows with all 'N/A' fields
    na_fields = selected_fields  # Fields selected for output
    save_to_excel_with_highlighting(df_processed, "updated_products.xlsx", na_fields)

    # Display completion message
    print(f"\nFile 'updated_products.xlsx' generated successfully.")

if __name__ == "__main__":
    main()
