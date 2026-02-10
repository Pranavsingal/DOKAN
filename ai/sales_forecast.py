import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import numpy as np

def predict_sales(items):
    sales_df = pd.read_csv('data/sales.csv')
    predictions = {}

    # Assume past 3 days of data
    forecast_days = 3
    cutoff_date = pd.to_datetime(sales_df['date'].max()) - timedelta(days=forecast_days)

    for item in items:
        item_id = str(item['id'])
        item_sales = sales_df[sales_df['item_id'].astype(str) == item_id]

        if item_sales.empty:
            predictions[item['name']] = 0
            continue

        # Prepare training data: use index as pseudo "day"
        item_sales['date'] = pd.to_datetime(item_sales['date'])
        item_sales = item_sales.sort_values(by='date')

        x = np.arange(len(item_sales)).reshape(-1, 1)
        y = item_sales['sales'].values

        if len(x) < 2:
            predictions[item['name']] = int(np.mean(y))  # fallback
            continue

        model = LinearRegression()
        model.fit(x, y)
        next_day = [[len(x)]]
        prediction = model.predict(next_day)[0]

        predictions[item['name']] = max(int(round(prediction)), 0)

    return predictions
