import pandas as pd
from User.models import OrderItem

def load_seller_product_sales(seller_id):
    qs = OrderItem.objects.select_related(
        'order',
        'product'
    ).filter(
        product__seller_id=seller_id     # 🔒 SELLER FILTER
    ).values(
        'product_id',
        'product__product_name',
        'quantity',
        'price',
        'order__created_at'
    )

    df = pd.DataFrame(qs)

    if df.empty:
        return df

    df.rename(columns={
        'product__product_name': 'product_name',
        'order__created_at': 'created_at'
    }, inplace=True)

    df['created_at'] = pd.to_datetime(df['created_at'])
    return df
