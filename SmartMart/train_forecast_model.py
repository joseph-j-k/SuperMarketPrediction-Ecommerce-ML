import os
import pandas as pd
import pickle
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(BASE_DIR, "product_monthly_forecast_dataset.csv")
model_folder = os.path.join(BASE_DIR, "ml_models")
model_path = os.path.join(model_folder, "sales_forecast_model.pkl")

if not os.path.exists(model_folder):
    os.makedirs(model_folder)

df = pd.read_csv(dataset_path)

feature_cols = [
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
]

target_col = "target_next_month_units"

X = df[feature_cols]
y = df[target_col]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42
)

model.fit(X_train, y_train)

preds = model.predict(X_test)

print("MAE:", mean_absolute_error(y_test, preds))
print("MSE:", mean_squared_error(y_test, preds))

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully at:")
print(model_path)