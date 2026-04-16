def add_time_features(df):
    df = df.sort_values(['product_id', 'year', 'month'])

    df['lag_1'] = df.groupby('product_id')['sold_units'].shift(1)
    df['lag_2'] = df.groupby('product_id')['sold_units'].shift(2)
    df['rolling_3'] = (
        df.groupby('product_id')['sold_units']
        .rolling(3)
        .mean()
        .reset_index(0, drop=True)
    )

    df.fillna(0, inplace=True)
    return df
