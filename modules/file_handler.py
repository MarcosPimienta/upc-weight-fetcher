import pandas as pd

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
