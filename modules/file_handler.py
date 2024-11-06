import pandas as pd

def load_excel(file_path):
    """Loads Excel data into a DataFrame."""
    return pd.read_excel(file_path)

def save_to_excel(df, file_path):
    """Saves DataFrame to an Excel file."""
    df.to_excel(file_path, index=False)

def save_to_csv(df, file_path):
    """Saves DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)
