import pandas as pd
from openpyxl.styles import PatternFill
from openpyxl import load_workbook

def load_excel(file_path, sheet_name=0, header_row=None):
    """
    Loads data from a specific sheet and header row in an Excel file into a DataFrame.

    Parameters:
    - file_path: Path to the Excel file.
    - sheet_name: The sheet name or index to load data from.
    - header_row: Row number (0-indexed) to use as the header. None if the first row.

    Returns:
    - DataFrame with the loaded data.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

def save_to_excel(df, file_path):
    """Saves DataFrame to an Excel file."""
    df.to_excel(file_path, index=False)

def save_to_csv(df, file_path):
    """Saves DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)

def sanitize_dataframe(df):
    """
    Replaces problematic characters in the DataFrame to avoid errors during saving.

    Parameters:
    - df: The DataFrame to sanitize.

    Returns:
    - A sanitized DataFrame with empty values instead of problematic placeholders.
    """
    return df.applymap(lambda x: "" if pd.isnull(x) or x == "N/A" else x)

def save_to_excel_with_highlighting(df, file_path, na_fields):
    """
    Saves a DataFrame to an Excel file and highlights rows with all selected fields empty in red.

    Parameters:
    - df: The DataFrame to save.
    - file_path: The path for the output Excel file.
    - na_fields: The list of fields to check for empty values.
    """
    # Sanitize DataFrame
    df = sanitize_dataframe(df)

    # Save the DataFrame to an Excel file
    df.to_excel(file_path, index=False, engine="openpyxl")

    # Apply red fill for rows with all selected fields empty
    red_fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
    wb = load_workbook(file_path)
    ws = wb.active

    # Iterate over rows and apply highlighting
    for row_idx, row in enumerate(df.itertuples(index=False), start=2):  # Start at 2 (row 1 is header)
        if all(getattr(row, field, "").strip() == "" for field in na_fields):
            for col_idx in range(1, len(df.columns) + 1):  # Apply fill to all columns
                ws.cell(row=row_idx, column=col_idx).fill = red_fill

    wb.save(file_path)
