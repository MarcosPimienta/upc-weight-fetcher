import sys
import pandas as pd
import inquirer
from modules.data_fetcher import (
    fetch_weight_from_upcitemdb_search,
    fetch_weights_from_red_circle,
    fetch_weights_from_go_upc,
)
from modules.data_converter import convert_to_grams
from modules.file_handler import save_to_excel, save_to_csv
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
            validate=lambda _, x: x.isdigit() and int(x) > 0,
        ),
    ]
    api_answers = inquirer.prompt(api_question)
    api_choice = api_answers["api_choice"]
    throttle_time = int(api_answers["throttle_time"])  # Convert input to integer

    # Step 3: Test API Connection
    print(f"\nTesting connection for {api_choice} API...")
    test_query = "Test Query Product"
    if api_choice == "UPCItemDB":
        # Pass empty lists for counters during the test
        test_response = fetch_weight_from_upcitemdb_search(test_query, api_key, throttle_time, [], [])
    elif api_choice == "RedCircle":
        test_response = fetch_weights_from_red_circle(test_query, api_key, throttle_time)
    elif api_choice == "Go-UPC":
        test_response = fetch_weights_from_go_upc("123456789012", api_key, throttle_time)
    else:
        print("Invalid API selection.")
        sys.exit(1)

    if not test_response:
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
    column_choices = inquirer.Checkbox(
        "columns",
        message="Select the columns you want to include in the output",
        choices=df.columns.tolist(),
    )
    selected_columns = inquirer.prompt([column_choices])["columns"]

    if not selected_columns:
        print("No columns selected. Exiting.")
        sys.exit(1)

    # Step 7: Ensure 'Title' column is included in the selected columns
    if "Title" not in df.columns:
        print("Error: Required column 'Title' not found in the data.")
        sys.exit(1)

    # Step 8: Process the data
    processed_data = []
    success_counter = []
    failure_counter = []

    for _, row in df.iterrows():
        title = row.get("Title", "").strip()

        # Fetch product details based on the selected API
        product_details = None
        if api_choice == "UPCItemDB":
            product_details = fetch_weight_from_upcitemdb_search(
                title, api_key, throttle_time, success_counter, failure_counter
            )
        elif api_choice == "RedCircle":
            product_details = fetch_weights_from_red_circle(
                title, api_key, throttle_time
            )
            if product_details:
                success_counter.append(1)
            else:
                failure_counter.append(1)
        elif api_choice == "Go-UPC":
            product_details = fetch_weights_from_go_upc(
                title, api_key, throttle_time
            )
            if product_details:
                success_counter.append(1)
            else:
                failure_counter.append(1)

        if product_details:
            weight_in_grams = None
            if product_details.get("weight"):
                # Attempt to split weight into value and unit
                weight_parts = product_details["weight"].split()
                if len(weight_parts) >= 2:
                    weight_value, weight_unit = weight_parts[:2]
                    weight_in_grams = convert_to_grams(float(weight_value), weight_unit)
                else:
                    print(f"{Fore.YELLOW}Warning: Unable to process weight for product '{title}': {product_details['weight']}{Style.RESET_ALL}")

            processed_row = {
                "title": product_details.get("title", "N/A"),
                "upc": product_details.get("upc", "N/A"),
                "brand": product_details.get("brand", "N/A"),
                "weight (grams)": weight_in_grams if weight_in_grams else "N/A",
                "category": product_details.get("category", "N/A"),
                "description": product_details.get("description", "N/A"),
                "images": ", ".join(product_details.get("images", [])),
            }
        else:
            processed_row = {
                "title": title,
                "upc": "N/A",
                "brand": "N/A",
                "weight (grams)": "N/A",
                "category": "N/A",
                "description": "N/A",
                "images": "N/A",
            }

        # Include additional selected columns
        for col in selected_columns:
            if col not in processed_row:
                processed_row[col] = row.get(col, "N/A")

        processed_data.append(processed_row)

    # Step 9: Save to new files
    output_df = pd.DataFrame(processed_data)
    save_to_csv(output_df, "updated_products.csv")
    save_to_excel(output_df, "updated_products.xlsx")

    # Step 10: Display summary
    print(f"\nFiles 'updated_products.csv' and 'updated_products.xlsx' generated successfully.")
    print(f"\n{len(success_counter)} products successfully processed.")
    print(f"{len(failure_counter)} products failed to process.")


if __name__ == "__main__":
    main()
