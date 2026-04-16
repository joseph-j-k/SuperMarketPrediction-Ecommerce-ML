import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(BASE_DIR, "Ecommerce_Sales_Data_2024_2025.csv")
output_file = os.path.join(BASE_DIR, "product_monthly_forecast_dataset.csv")

df = pd.read_csv(input_file)

print("Original Columns:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

# =========================
# CLEAN DATA
# =========================
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
df = df.dropna(subset=["Order Date"])

df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0)
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)
df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)
df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0)

df["year"] = df["Order Date"].dt.year
df["month"] = df["Order Date"].dt.month
df["quarter"] = ((df["month"] - 1) // 3) + 1

# create product_id from product name
df["product_id"] = df["Product Name"].astype("category").cat.codes

# =========================
# MONTHLY PRODUCT SUMMARY
# =========================
monthly_df = (
    df.groupby(
        ["product_id", "Product Name", "year", "month", "quarter"],
        as_index=False
    )
    .agg(
        sold_units=("Quantity", "sum"),
        revenue=("Sales", "sum"),
        avg_price=("Unit Price", "mean"),
        avg_discount=("Discount", "mean"),
        total_profit=("Profit", "sum")
    )
    .sort_values(["product_id", "year", "month"])
    .reset_index(drop=True)
)

print("\nMonthly Summary:")
print(monthly_df.head())

# =========================
# LAG FEATURES
# =========================
monthly_df["previous_month_units"] = (
    monthly_df.groupby(["product_id"])["sold_units"].shift(1)
)

monthly_df["previous_2_month_avg"] = (
    monthly_df.groupby(["product_id"])["sold_units"]
    .transform(lambda x: x.shift(1).rolling(2).mean())
)

monthly_df["previous_3_month_avg"] = (
    monthly_df.groupby(["product_id"])["sold_units"]
    .transform(lambda x: x.shift(1).rolling(3).mean())
)

monthly_df["previous_month_revenue"] = (
    monthly_df.groupby(["product_id"])["revenue"].shift(1)
)

monthly_df["previous_month_profit"] = (
    monthly_df.groupby(["product_id"])["total_profit"].shift(1)
)

monthly_df["previous_month_units"] = monthly_df["previous_month_units"].fillna(0)
monthly_df["previous_2_month_avg"] = monthly_df["previous_2_month_avg"].fillna(0)
monthly_df["previous_3_month_avg"] = monthly_df["previous_3_month_avg"].fillna(0)
monthly_df["previous_month_revenue"] = monthly_df["previous_month_revenue"].fillna(0)
monthly_df["previous_month_profit"] = monthly_df["previous_month_profit"].fillna(0)

# =========================
# TARGET
# =========================
monthly_df["target_next_month_units"] = (
    monthly_df.groupby(["product_id"])["sold_units"].shift(-1)
)

train_df = monthly_df.dropna(subset=["target_next_month_units"]).copy()
train_df["target_next_month_units"] = train_df["target_next_month_units"].astype(int)

final_columns = [
    "product_id",
    "Product Name",
    "year",
    "month",
    "quarter",
    "sold_units",
    "revenue",
    "avg_price",
    "avg_discount",
    "total_profit",
    "previous_month_units",
    "previous_2_month_avg",
    "previous_3_month_avg",
    "previous_month_revenue",
    "previous_month_profit",
    "target_next_month_units",
]

train_df = train_df[final_columns]

print("\nTraining Dataset:")
print(train_df.head())
print("\nShape:", train_df.shape)

train_df.to_csv(output_file, index=False)

print("\nModified dataset saved successfully as:")
print(output_file)