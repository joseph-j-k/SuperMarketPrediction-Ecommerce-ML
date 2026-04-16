import pickle
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ml_models" / "sales_forecast_model.pkl"


def load_forecast_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    return model


def forecast_seller_products(monthly_df):
    """
    Forecast next month sales per product.
    Uses fallback average when history is too small.
    """

    if monthly_df.empty:
        return monthly_df

    model = load_forecast_model()
    results = []

    grouped = monthly_df.groupby("product_id")

    for product_id, group in grouped:
        group = group.sort_values(["year", "month"]).copy()
        latest = group.tail(1).copy()

        # move to next month
        latest["month"] += 1
        rollover = latest["month"] > 12
        latest.loc[rollover, "month"] = 1
        latest.loc[rollover, "year"] += 1
        latest["quarter"] = ((latest["month"] - 1) // 3) + 1

        # update lag values from last known sales
        latest["previous_month_units"] = latest["sold_units"]
        latest["previous_month_revenue"] = latest["revenue"]
        latest["previous_month_profit"] = latest["total_profit"]

        latest["previous_2_month_avg"] = latest["previous_2_month_avg"].fillna(latest["sold_units"])
        latest["previous_3_month_avg"] = latest["previous_3_month_avg"].fillna(latest["sold_units"])
        latest["avg_discount"] = latest["avg_discount"].fillna(0)
        latest["avg_price"] = latest["avg_price"].fillna(0)
        latest["total_profit"] = latest["total_profit"].fillna(0)
        latest["previous_month_units"] = latest["previous_month_units"].fillna(0)
        latest["previous_month_revenue"] = latest["previous_month_revenue"].fillna(0)
        latest["previous_month_profit"] = latest["previous_month_profit"].fillna(0)

        # -------- FALLBACK LOGIC --------
        # If very little history, use simple dynamic average instead of ML
        if len(group) < 3:
            fallback_value = round(group["sold_units"].mean()) if len(group) > 0 else 0
            latest["predicted_units"] = max(0, fallback_value)
        else:
            X = latest[[
                "product_id",
                "year",
                "month",
                "quarter",
                "avg_price",
                "avg_discount",
                "total_profit",
                "previous_month_units",
                "previous_2_month_avg",
                "previous_3_month_avg",
                "previous_month_revenue",
                "previous_month_profit",
            ]]

            preds = model.predict(X)
            preds = np.clip(preds, 0, None)
            latest["predicted_units"] = preds.round().astype(int)

        results.append(latest[[
            "product_id",
            "product_name",
            "year",
            "month",
            "predicted_units"
        ]])

    final_df = np.concatenate([r.values for r in results], axis=0)

    import pandas as pd
    final_df = pd.DataFrame(final_df, columns=[
        "product_id",
        "product_name",
        "year",
        "month",
        "predicted_units"
    ])

    final_df["product_id"] = final_df["product_id"].astype(int)
    final_df["year"] = final_df["year"].astype(int)
    final_df["month"] = final_df["month"].astype(int)
    final_df["predicted_units"] = final_df["predicted_units"].astype(int)

    return final_df