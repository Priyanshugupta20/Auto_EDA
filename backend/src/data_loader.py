import os
import pandas as pd
import logging

def load_data(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.csv':
            return pd.read_csv(filepath)
        elif file_ext == '.xls':
            return pd.read_excel(filepath, engine='xlrd')
        elif file_ext == '.xlsx':
            return pd.read_excel(filepath, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        raise ValueError(f"Error loading file: {e}")


    return df
