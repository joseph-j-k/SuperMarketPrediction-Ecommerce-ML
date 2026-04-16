def monthly_product_sales(df):
    df['year'] = df['created_at'].dt.year
    df['month'] = df['created_at'].dt.month

    monthly = df.groupby(
        ['product_id', 'product_name', 'year', 'month']
    ).agg(
        sold_units=('quantity', 'sum'),
        revenue=('quantity', lambda x: (x * df.loc[x.index, 'price']).sum())
    ).reset_index()

    return monthly
