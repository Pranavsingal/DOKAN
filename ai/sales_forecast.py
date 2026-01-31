import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'dokan.db')

def forecast_sales(days=7):
    try:
        conn = sqlite3.connect(DB_PATH)
        # Query the SalesRecord table which matches sales.csv
        query = "SELECT date, sales FROM sales_record"
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty: return {}

        # Preprocessing
        df['date'] = pd.to_datetime(df['date'])
        # Group by date to get total sales per day across all items
        df_daily = df.groupby('date')['sales'].sum().reset_index()
        
        df_daily['date_ordinal'] = df_daily['date'].map(pd.Timestamp.toordinal)

        model = LinearRegression()
        model.fit(df_daily[['date_ordinal']], df_daily['sales'])

        last_date = df_daily['date'].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days + 1)]
        future_ordinal = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        
        predictions = model.predict(future_ordinal)
        
        return {
            "dates": [d.strftime('%Y-%m-%d') for d in future_dates],
            "sales": [round(p, 2) for p in predictions]
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {}