import sys
import pandas as pd
import inquirer
from modules.upcitem_fetcher import fetch_weight_from_upcitemdb_search
from modules.red_circle_fetcher import fetch_weights_from_red_circle
from modules.go_upc_fetcher import fetch_weights_from_go_upc
from modules.file_handler import save_to_excel_with_highlighting, sanitize_dataframe
from colorama import Fore, Style
import os


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

    # Step 3: Load Excel file and list available sheets
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

    # Step 4: Inquire the user about the row where column names are located
    column_row_question = [
        inquirer.Text(
            "header_row",
            message="Enter the row number where column names are located (e.g., 1 for first row)",
            validate=lambda _, x: x.isdigit() and int(x) > 0,
        )
    ]
    header_row = int(inquirer.prompt(column_row_question)["header_row"]) - 1  # Adjust for zero-based index

    # Step 5: Load the selected sheet with specified header row
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        df = sanitize_dataframe(df)  # Use sanitize_dataframe for preprocessing
    except Exception as e:
        print(f"Error loading sheet '{sheet_name}': {e}")
        sys.exit(1)

    # Step 6: Ask user to map the column holding the parameter for the query
    parameter_column_question = [
        inquirer.List(
            "parameter_column",
            message="Select the column that holds the parameter for API queries:",
            choices=df.columns.tolist(),
        )
    ]
    parameter_column = inquirer.prompt(parameter_column_question)["parameter_column"]

    # Step 7: Inquire about columns to migrate
    column_choices = ["None"] + df.columns.tolist()
    column_question = inquirer.Checkbox(
        "columns",
        message="Select the columns you want to include in the output:",
        choices=column_choices,
    )
    selected_columns = inquirer.prompt([column_question])["columns"]

    # If "None" is selected, clear the selected columns
    if "None" in selected_columns:
        selected_columns = []

    # Step 8: Process the data
    processed_data = []
    success_counter = []
    failure_counter = []

    # If RedCircle, inquire about the query type
    query_type = None
    if api_choice == "RedCircle":
        query_type_question = inquirer.List(
            "query_type",
            message="Select the query type for RedCircle API",
            choices=["search", "category", "product"],
        )
        query_type = inquirer.prompt([query_type_question])["query_type"]
        if query_type == "product":
            print(f"{Fore.YELLOW}Note: For 'product', the GTIN will be formatted from the UPC by prefixing '00'.{Style.RESET_ALL}")

    total_queries = len(df)  # Total number of queries
    for index, row in enumerate(df.itertuples(index=False), start=1):
        parameter_value = getattr(row, parameter_column, "").strip()

        # Format GTIN if RedCircle and product query
        if api_choice == "RedCircle" and query_type == "product":
            parameter_value = f"00{parameter_value}"

        # Display query progress
        print(f"{Fore.CYAN}Processing query {index}/{total_queries}: {parameter_value}{Style.RESET_ALL}")

        # Fetch product details based on the selected API
        product_details = None
        if api_choice == "UPCItemDB":
            product_details = fetch_weight_from_upcitemdb_search(
                parameter_value, api_key, throttle_time, success_counter, failure_counter
            )
        elif api_choice == "RedCircle":
            product_details = fetch_weights_from_red_circle(
                parameter_value, api_key, throttle_time, success_counter, failure_counter, query_type
            )
        elif api_choice == "Go-UPC":
            product_details = fetch_weights_from_go_upc(
                parameter_value, api_key, throttle_time, success_counter, failure_counter
            )

        # Prepare the row data
        processed_row = {col: getattr(row, col, "") for col in selected_columns}
        if product_details:
            processed_row.update({
                "parameter_value": parameter_value,
                "title": product_details.get("title", ""),
                "upc": product_details.get("upc", ""),
                "brand": product_details.get("brand", ""),
                "weight (grams)": product_details.get("weight", ""),
                "category": product_details.get("category", ""),
                "description": product_details.get("description", ""),
                "images": ", ".join(product_details.get("images", [])),
            })
        else:
            processed_row.update({
                "parameter_value": parameter_value,
                "title": "",
                "upc": "",
                "brand": "",
                "weight (grams)": "",
                "category": "",
                "description": "",
                "images": "",
            })

        processed_data.append(processed_row)

    # Step 9: Highlight empty rows and save results
    df_processed = pd.DataFrame(processed_data)
    na_fields = ["title", "description", "price", "sku", "brand", "category", "images"]
    output_dir = f"results/{api_choice.lower()}"
    os.makedirs(output_dir, exist_ok=True)
    save_to_excel_with_highlighting(
        df_processed, f"{output_dir}/{api_choice.lower()}_products.xlsx", na_fields
    )

    # Display summary
    print(f"\nFiles '{api_choice.lower()}_products.xlsx' generated successfully.")
    print(f"\n{len(success_counter)} products successfully processed.")
    print(f"{len(failure_counter)} products failed to process.")


if __name__ == "__main__":
    main()
