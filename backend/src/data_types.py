import pandas as pd
import logging

def fix_data_types(df):
    """
    Fixes common data type issues in the DataFrame:
    - Converts numeric-looking strings to numeric
    - Parses datetime strings to datetime64
    - Converts categorical-like columns to 'category'
    - Standardizes boolean columns
    - Strips whitespace from strings and column names
    - Logs all changes
    """
    df = df.copy()
    log = []

    for col in df.columns:
        original_dtype = df[col].dtype

        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):

            lower_vals = df[col].dropna().str.lower().unique()
            if set(lower_vals).issubset({'true', 'false', 'yes', 'no', '0', '1'}):
                df[col] = df[col].str.lower().map({
                    'true': True, 'yes': True, '1': True,
                    'false': False, 'no': False, '0': False
                })
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'bool',
                    'action': 'converted to boolean'
                })
                logging.info(f"Column '{col}' converted from {original_dtype} to boolean")
                continue
            
            try:
                print
                converted = pd.to_numeric(df[col], errors='raise')
                df[col] = converted
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'numeric',
                    'action': 'converted from string to numeric'
                })
                logging.info(f"Column '{col}' converted from {original_dtype} to numeric")
                continue
            except:
                pass

            try:
                # First, try parsing with a known format (fast and consistent)
                converted = pd.to_datetime(df[col], errors='raise', format='%Y-%m-%d')
                df[col] = converted
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'datetime',
                    'action': 'converted from string to datetime'
                })
                logging.info(f"Column '{col}' converted from {original_dtype} to datetime")
                continue
            except Exception:
                # Fall back to flexible parsing with 'coerce'
                converted = pd.to_datetime(df[col], errors='coerce')
                if converted.notna().sum() > 0:
                    df[col] = converted
                    log.append({
                        'column': col,
                        'from': str(original_dtype),
                        'to': 'datetime (partial)',
                        'action': 'some values converted to datetime; invalids coerced to NaT'
                    })
                    logging.warning(f"Column '{col}' had invalid datetime values. Converted valid ones; rest set as NaT.")
                    continue

            unique_count = df[col].nunique(dropna=True)
            total_count = len(df[col])
            if unique_count / total_count < 0.1:
                df[col] = df[col].astype('category')
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'category',
                    'action': f'converted to category ({unique_count} unique values)'
                })
                logging.info(f"Column '{col}' converted from {original_dtype} to category with {unique_count} unique values")
        elif pd.api.types.is_numeric_dtype(df[col]):
            unique_vals = df[col].dropna().unique()
            if set(unique_vals).issubset({0, 1}):
                df[col] = df[col].astype(bool)
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'bool',
                    'action': 'converted numeric 0/1 to boolean'
                })
                logging.info(f"Column '{col}' converted from {original_dtype} to boolean")
                continue

    return df, log

def identify_columns(df):

    col_types = {
        "numerical": [],
        "categorical": [],
        "datetime": [],
        "boolean": [],
        "others": []
    }

    for col in df.columns:
        if pd.api.types.is_bool_dtype(df[col]):
            col_types["boolean"].append(col)

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_types['datetime'].append(col)

        elif pd.api.types.is_numeric_dtype(df[col]):
            col_types['numerical'].append(col)

        elif isinstance(df[col].dtype, pd.CategoricalDtype):
            col_types['categorical'].append(col)

        else:
            col_types['others'].append(col)
    logging.info(col_types)

    return col_types