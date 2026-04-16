import pandas as pd
from vendor.models import Product
from User.models import OrderItem

def load_historical_sales_from_db():

    # 1️⃣ Products
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

    products_df.rename(columns={'id': 'product_id'}, inplace=True)

    # 2️⃣ Orders
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
        products_df['year'] = pd.Timestamp.now().year
        products_df['month'] = pd.Timestamp.now().month
        return products_df

    orders_df.rename(columns={'order__created_at': 'created_at'}, inplace=True)
    orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])

    # 3️⃣ Revenue (SAFE)
    orders_df['revenue'] = orders_df['quantity'] * orders_df['price']
    orders_df['year'] = orders_df['created_at'].dt.year
    orders_df['month'] = orders_df['created_at'].dt.month

    sales_summary = orders_df.groupby(
        ['product_id', 'year', 'month'],
        as_index=False
    ).agg(
        sold_units=('quantity', 'sum'),
        revenue=('revenue', 'sum')
    )

    # 4️⃣ LEFT JOIN
    df = products_df.merge(
        sales_summary,
        on='product_id',
        how='left'
    )

    # 5️⃣ Fill gaps
    df['sold_units'] = df['sold_units'].fillna(0).astype(int)
    df['revenue'] = df['revenue'].fillna(0)
    df['year'] = df['year'].fillna(pd.Timestamp.now().year).astype(int)
    df['month'] = df['month'].fillna(pd.Timestamp.now().month).astype(int)

    # 6️⃣ Unsold units
    df['unsold_units'] = df['stock'] - df['sold_units']
    df['unsold_units'] = df['unsold_units'].clip(lower=0)

    return df


def prepare_historical_summary(df):
    summary = df.groupby(
        ['product_id', 'product_name', 'seller_id', 'year', 'month'],
        as_index=False
    ).agg(
        sold_units=('sold_units', 'sum'),
        unsold_units=('unsold_units', 'sum'),
        revenue=('revenue', 'sum')
    )

    return summary
