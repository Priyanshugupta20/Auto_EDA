from utils.config import OUTPUT_FOLDER
import logging

def log_cleaning_report(df_before, df_after):
    pass

def save_cleaned_data(df, filename='cleaned_data.csv'):
    cleaned_path = OUTPUT_FOLDER / filename
    df.to_csv(cleaned_path, index=False)
    logging.info(f"Saved cleaned dataset to {cleaned_path}")

    return filename
