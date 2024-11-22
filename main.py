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
            validate=lambda _, x: x.isdigit() and int(x) >= 0,
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
    column_choices = ["None"] + df.columns.tolist()  # Add "None" as the first option
    column_question = inquirer.Checkbox(
        "columns",
        message="Select the columns you want to include in the output:",
        choices=column_choices,
    )
    selected_columns = inquirer.prompt([column_question])["columns"]

    # If "None" is selected, clear the selected columns
    if "None" in selected_columns:
        selected_columns = []

    # Step 7: Ensure 'Title' column is included in the selected columns
    if "Title" not in df.columns:
        print("Error: Required column 'Title' not found in the data.")
        sys.exit(1)

    # Step 8: Process the data
    processed_data = []
    success_counter = []
    failure_counter = []

    total_queries = len(df)  # Total number of queries
    for index, row in enumerate(df.iterrows(), start=1):
        title = row[1].get("Title", "").strip()

        # Display query progress
        print(f"{Fore.CYAN}Processing query {index}/{total_queries}: {title}{Style.RESET_ALL}")

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
                product_details["risky"] = "No"  # RedCircle doesn't have retry logic
                success_counter.append(1)
            else:
                failure_counter.append(1)
        elif api_choice == "Go-UPC":
            product_details = fetch_weights_from_go_upc(
                title, api_key, throttle_time
            )
            if product_details:
                product_details["risky"] = "No"  # Go-UPC doesn't have retry logic
                success_counter.append(1)
            else:
                failure_counter.append(1)

        if product_details:
            weight_in_grams = None
            if product_details.get("weight"):
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
                "risky": product_details.get("risky", "N/A"),
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
                "risky": "N/A",
            }

        # Include additional selected columns
        for col in selected_columns:
            if col not in processed_row:
                processed_row[col] = row[1].get(col, "N/A")

        processed_data.append(processed_row)

    # Step 9: Categorize the processed data
    general_report = processed_data
    positive_products = [row for row in processed_data if row.get("risky") == "No"]
    risky_products = [row for row in processed_data if row.get("risky") == "Yes"]
    failed_products = [row for row in processed_data if row.get("upc") == "N/A"]

    # Step 10: Save to Excel with multiple sheets
    with pd.ExcelWriter("updated_products.xlsx") as writer:
        # General report
        pd.DataFrame(general_report).to_excel(writer, sheet_name="general_report", index=False)
        # Positive products
        pd.DataFrame(positive_products).to_excel(writer, sheet_name="positive_products", index=False)
        # Risky products
        pd.DataFrame(risky_products).to_excel(writer, sheet_name="risky_products", index=False)
        # Failed products
        pd.DataFrame(failed_products).to_excel(writer, sheet_name="failed_products", index=False)

    # Step 11: Save to CSV (general report only)
    save_to_csv(pd.DataFrame(general_report), "updated_products.csv")

    # Step 12: Display summary
    print(f"\nFiles 'updated_products.csv' and 'updated_products.xlsx' generated successfully.")
    print(f"\n{len(success_counter)} products successfully processed.")
    print(f"{len(failure_counter)} products failed to process.")
    print(f"{len(positive_products)} products fetched on the first attempt.")
    print(f"{len(risky_products)} products fetched after retries.")
    print(f"{len(failed_products)} products failed to fetch.")

if __name__ == "__main__":
    main()
