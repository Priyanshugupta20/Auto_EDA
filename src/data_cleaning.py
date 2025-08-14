import pandas as pd
import numpy as np

def handle_missing_values(df, numerical_cols, categorical_cols, col_drop_thresh=0.5):
    """
    - Converting empty strings and whitespace to NaN
    - Dropping columns with too many missing values
    - Imputing numeric columns with median
    - Imputing categorical columns with mode or 'Unknown'
    """
    df = df.copy()
    log = []

    for col in categorical_cols:
        if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].replace(r'^\s*$', np.nan, regex=True)

    cols_to_drop = []
    for col in df.columns:
        missing_ratio = df[col].isna().mean()
        if missing_ratio >= col_drop_thresh:
            cols_to_drop.append(col)
            log.append({
                'column': col,
                'action': 'dropped',
                'reason': f'{round(missing_ratio * 100, 2)}% missing'
            })

    df.drop(columns=cols_to_drop, inplace=True)
    
    numerical_cols = [col for col in numerical_cols if col not in cols_to_drop]
    categorical_cols = [col for col in categorical_cols if col not in cols_to_drop]

    for col in numerical_cols:
        if df[col].isna().sum() > 0:
            median_value = df[col].median()
            df[col].fillna(median_value, inplace=True)
            log.append({
                'column': col,
                'action': 'imputed',
                'method': 'median',
                'value_used': median_value,
                'missing_count': int(df[col].isna().sum())
            })

    for col in categorical_cols:
        if df[col].isna().sum() > 0:
            try:
                mode_value = df[col].mode()[0]
            except IndexError:
                mode_value = 'Unknown'
            df[col].fillna(mode_value, inplace=True)
            log.append({
                'column': col,
                'action': 'imputed',
                'method': 'mode',
                'value_used': mode_value,
                'missing_count': int(df[col].isna().sum())
            })

    return df, log

def remove_duplicates(df):
    pass

def handle_outliers(df):
    pass

def normalize_text_columns(df):
    pass
