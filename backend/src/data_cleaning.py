import pandas as pd
import numpy as np
import logging

def normalize_text_columns(df, other_cols:list):
    """
    Normalize all text columns in the DataFrame:
    - Convert to string
    - Strip leading/trailing whitespace
    - Convert to lowercase
    """
    df = df.copy()

    for col in other_cols:
        df[col] = df[col].where(df[col].isna(), df[col].astype(str).str.strip().str.lower())

    return df

def remove_duplicates(
    df: pd.DataFrame,
    subset: list = None,
    keep: str = 'first',
    timestamp_col: str = None,
) -> pd.DataFrame:
    """
    Remove duplicate rows from the DataFrame after normalizing text columns.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - subset (list): Optional. Columns to check for duplicates. If None, use all columns.
    - keep (str): 'first', 'last', 'latest', or False. Which duplicate to keep.
    - timestamp_col (str): Required if keep='latest'. Column used to decide latest row.
    - log (bool): Whether to print a log summary.

    Returns:
    - pd.DataFrame: Deduplicated DataFrame.
    - Log: list of dict
    """
    df = df.copy()
    log = []
    if keep == 'latest':
        if not timestamp_col:
            raise ValueError("You must provide 'timestamp_col' when keep='latest'")
        if timestamp_col not in df.columns:
            raise ValueError(f"'{timestamp_col}' not found in DataFrame columns")

        # Sort so latest comes first
        df = df.sort_values(by=timestamp_col, ascending=False)
        keep = 'first'

    original_count = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep)
    new_count = len(df)
    duplicates_removed = original_count - new_count

    used_cols = subset if subset else "all columns"
    logging.info(f"[remove_duplicates] Removed {duplicates_removed} duplicates using {used_cols}, keep='{keep}'")
    if duplicates_removed != 0:
        log.append({
            'action': 'remove_duplicates',
            'duplicates_removed': duplicates_removed,
            'original_row_count': original_count,
            'new_row_count': new_count,
            'message': f"Removed {duplicates_removed} duplicate rows."
        })

    return df, log

def handle_missing_values(df, numerical_cols, categorical_cols, datetime_cols, col_drop_thresh=0.5):
    """
    - Converting empty strings and whitespace to NaN
    - Dropping columns with too many missing values
    - Imputing numeric columns with median
    - Imputing categorical columns with mode or 'Unknown'
    """
    df = df.copy()
    log = []

    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
            empty_count = df[col].str.strip().eq('').sum()
            if empty_count > 0:
                logging.info(f"Column '{col}': Converted {empty_count} empty strings to NaN")
            df[col] = df[col].replace(r'^\s*$', np.nan, regex=True)

    cols_to_drop = []
    for col in df.columns:
        missing_ratio = df[col].isna().mean()
        if missing_ratio >= col_drop_thresh:
            cols_to_drop.append(col)
            logging.warning(f"Dropping column '{col}' with {missing_ratio:.2%} missing values")
            log.append({
                'column': col,
                'action': 'dropped',
                'reason': f'{round(missing_ratio * 100, 2)}% missing'
            })

    df.drop(columns=cols_to_drop, inplace=True)
    
    numerical_cols = [col for col in numerical_cols if col not in cols_to_drop]
    categorical_cols = [col for col in categorical_cols if col not in cols_to_drop]
    datetime_cols = [col for col in datetime_cols if col in df.columns]

    for col in numerical_cols:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            median_value = df[col].median()
            df[col].fillna(median_value, inplace=True)
            logging.info(f"Imputed {missing_count} missing values in numeric column '{col}' with median = {median_value}")
            log.append({
                'column': col,
                'action': 'imputed',
                'method': 'median',
                'value_used': median_value,
                'missing_count': int(missing_count)
            })

    for col in categorical_cols:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            try:
                mode_value = df[col].mode()[0]
            except IndexError:
                mode_value = 'Unknown'
            df[col].fillna(mode_value, inplace=True)
            logging.info(f"Imputed {missing_count} missing values in categorical column '{col}' with mode = '{mode_value}'")
            log.append({
                'column': col,
                'action': 'imputed',
                'method': 'mode',
                'value_used': mode_value,
                'missing_count': int(missing_count)
            })
            
    for col in datetime_cols:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            try:
                median_date = df[col].dropna().median()
                df[col].fillna(median_date, inplace=True)
                method = 'median'
                value_used = median_date
            except Exception:
                default_date = pd.to_datetime("1970-01-01")
                df[col].fillna(default_date, inplace=True)
                method = 'default_date'
                value_used = default_date

            logging.info(f"Imputed {missing_count} missing values in datetime column '{col}' with {method} = {value_used}")
            log.append({
                'column': col,
                'action': 'imputed',
                'method': method,
                'value_used': str(value_used),
                'missing_count': int(missing_count)
            })
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col].fillna('empty', inplace=True)
    
    return df, log

def handle_outliers(df):
    df = df.copy()
    log = []

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        # Detect outliers
        outliers_below = (df[col] < lower).sum()
        outliers_above = (df[col] > upper).sum()
        total_outliers = outliers_below + outliers_above

        # Log if there are outliers
        if total_outliers > 0:
            log.append({
                'column': col,
                'outliers_below': int(outliers_below),
                'outliers_above': int(outliers_above),
                'total_outliers': int(total_outliers),
                'lower_bound': lower,
                'upper_bound': upper,
                'action': f'Clipped to [{lower}, {upper}]'
            })

        # Clip the values
        df[col] = df[col].clip(lower, upper)

    return df, log
