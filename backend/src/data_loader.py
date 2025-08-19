import os
import pandas as pd
import logging

def load_data(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
            logging.info(f"Loaded CSV file: {file_path} with shape {df.shape}")
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
            logging.info(f"Loaded Excel file: {file_path} with shape {df.shape}")
        else:
            msg = f"Unsupported file extension: {ext}"
            logging.error(msg)
            raise ValueError(msg)
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        raise ValueError(f"Error loading file: {e}")

    return df