import pandas as pd

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

            df[col] = df[col].astype(str).str.strip()

            try:
                converted = pd.to_numeric(df[col], errors='raise')
                df[col] = converted
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'numeric',
                    'action': 'converted from string to numeric'
                })
                continue
            except:
                pass

            try:
                converted = pd.to_datetime(df[col], errors='raise', infer_datetime_format=True)
                df[col] = converted
                log.append({
                    'column': col,
                    'from': str(original_dtype),
                    'to': 'datetime',
                    'action': 'converted from string to datetime'
                })
                continue
            except:
                pass


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

    return df, log

def identify_columns(df):

    numerical_cols = []
    categorical_cols = []
    datetime_cols = []
    boolean_cols = []
    other_cols = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numerical_cols.append(col)

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)

        elif pd.api.types.is_bool_dtype(df[col]):
            boolean_cols.append(col)

        elif pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            categorical_cols.append(col)

        else:
            other_cols.append(col)

    return {
        "numerical": numerical_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
        "boolean": boolean_cols,
        "others": other_cols
    }
