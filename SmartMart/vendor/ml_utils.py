from vendor.models import Product
from User.models import OrderItem

def load_historical_sales_from_db():
    import pandas as pd

    products_qs = Product.objects.select_related(
        'seller'
    ).values(
        'id',
        'product_name',
        'seller_id',
        'stock'
    )

    products_df = pd.DataFrame(products_qs)

    if products_df.empty:
        return products_df

    products_df.rename(columns={
        'id': 'product_id'
    }, inplace=True)

    orders_qs = OrderItem.objects.select_related(
        'order'
    ).values(
        'product_id',
        'quantity',
        'price',
        'order__created_at'
    )

    orders_df = pd.DataFrame(orders_qs)

    if orders_df.empty:
        products_df['sold_units'] = 0
        products_df['revenue'] = 0
        products_df['unsold_units'] = products_df['stock']
        return products_df

    orders_df.rename(columns={
        'order__created_at': 'created_at'
    }, inplace=True)

    orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])

    orders_df['year'] = orders_df['created_at'].dt.year
    orders_df['month'] = orders_df['created_at'].dt.month

    sales_summary = orders_df.groupby(
        ['product_id', 'year', 'month']
    ).agg(
        sold_units=('quantity', 'sum'),
        revenue=('quantity', lambda x: (x * orders_df.loc[x.index, 'price']).sum())
    ).reset_index()

    df = products_df.merge(
        sales_summary,
        on='product_id',
        how='left'
    )

    df['sold_units'] = df['sold_units'].fillna(0).astype(int)
    df['revenue'] = df['revenue'].fillna(0)
    df['year'] = df['year'].fillna(pd.Timestamp.now().year).astype(int)
    df['month'] = df['month'].fillna(pd.Timestamp.now().month).astype(int)

    df['unsold_units'] = df['stock'] - df['sold_units']
    df['unsold_units'] = df['unsold_units'].clip(lower=0)

    return df


def prepare_historical_summary(df):
    import pandas as pd

    df['year'] = df['created_at'].dt.year
    df['month'] = df['created_at'].dt.month

    summary = df.groupby(
        ['product_id', 'product_name', 'seller_id', 'year', 'month', 'stock']
    ).agg(
        sold_units=('quantity', 'sum'),
        revenue=('quantity', lambda x: (x * df.loc[x.index, 'price']).sum())
    ).reset_index()

    summary['unsold_units'] = summary['stock'] - summary['sold_units']
    summary['unsold_units'] = summary['unsold_units'].clip(lower=0)

    return summary


def generate_future_months(last_year, last_month, periods=3):
    import pandas as pd

    future = []

    for i in range(1, periods + 1):
        month = last_month + i
        year = last_year

        if month > 12:
            month -= 12
            year += 1

        future.append({
            'year': year,
            'month': month
        })

    return pd.DataFrame(future)


def baseline_forecast(summary_df, periods=3):
    import pandas as pd

    forecast_rows = []

    for product_id in summary_df['product_id'].unique():
        product_df = summary_df[
            summary_df['product_id'] == product_id
        ].sort_values(['year', 'month'])

        avg_sold = product_df['sold_units'].tail(3).mean()

        last_year = product_df.iloc[-1]['year']
        last_month = product_df.iloc[-1]['month']

        future_df = generate_future_months(last_year, last_month, periods)

        for _, row in future_df.iterrows():
            forecast_rows.append({
                'product_id': product_id,
                'product_name': product_df.iloc[0]['product_name'],
                'year': int(row['year']),
                'month': int(row['month']),
                'forecast_units': int(round(avg_sold))
            })

    return pd.DataFrame(forecast_rows)