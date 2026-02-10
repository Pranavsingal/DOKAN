import pandas as pd

def predict_stockout(items):
    stockout_predictions = []

    try:
        # Load sales data
        sales_data = pd.read_csv('data/sales.csv')
    except Exception as e:
        print(f"❌ Failed to read sales data: {e}")
        return []

    # Iterate over each item in the provided list
    for item in items:
        try:
            item_id = item.get('id')
            stock = float(item.get('stock', 0))

            # Filter sales data for the item
            item_sales = sales_data[sales_data['item_id'] == item_id]

            # If no sales data for the item, skip it
            if item_sales.empty or stock <= 0:
                continue

            # Ensure sales column is numeric and handle errors
            item_sales['sales'] = pd.to_numeric(item_sales['sales'], errors='coerce').fillna(0)

            # Calculate average daily sales (mean of daily sales)
            daily_sales = item_sales.groupby('date')['sales'].sum().mean()

            if daily_sales > 0:
                # Calculate days until stockout
                days_until_stockout = int(stock / daily_sales)
                stockout_predictions.append({
                    'item': item['name'],
                    'days_until_stockout': days_until_stockout
                })
                print(f"Prediction for {item['name']}: {days_until_stockout} days until stockout")  # Debugging output

        except Exception as e:
            print(f"⚠️ Error processing item '{item.get('name')}': {e}")

    if not stockout_predictions:
        print("No stockout predictions available")  # Debugging output
    return stockout_predictions
