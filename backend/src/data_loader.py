import os
import pandas as pd

def load_data(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")

    return df