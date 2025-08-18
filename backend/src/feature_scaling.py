from sklearn.preprocessing import MinMaxScaler

def scale_numerical_columns(df):
    """Scale all numeric columns between 0 and 1."""
    scaler = MinMaxScaler()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = scaler.fit_transform(df[num_cols])
    return df
