from flask import Flask, render_template, request, redirect, url_for
import csv, os
from ai.sales_forecast import predict_sales
from ai.stockout_predictor import predict_stockout
from ai.recommender import recommend_products
from ai.categorizer import categorize_product
from ai.sentiment_analyzer import analyze_feedback

app = Flask(__name__)
CSV_FILE = 'data/inventory.csv'
SALES_FILE = 'data/sales.csv'
FEEDBACK_FILE = 'data/feedback.csv'


# Helper functions for reading and writing CSV
def read_csv(file_path):
    with open(file_path, mode='r', newline='') as file:
        return list(csv.DictReader(file))


def write_csv(file_path, data):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


@app.route('/')
def home():
    return redirect(url_for('inventory'))


@app.route('/inventory', methods=['GET', 'POST'])
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    items = read_csv(CSV_FILE)

    if request.method == 'POST':
        item = {
            'id': request.form['id'],
            'name': request.form['name'],
            'category': request.form['category'],
            'stock': request.form['stock'],
            'price': request.form['price'],
            'expiry_date': request.form['expiry_date'],
            'supplier': request.form['supplier']
        }

        data = read_csv(CSV_FILE)
        for i, row in enumerate(data):
            if row['id'] == item['id']:
                data[i] = item
                break
        else:
            data.append(item)
        write_csv(CSV_FILE, data)
        return redirect(url_for('inventory'))

    # No AI/ML Integration here anymore
    return render_template('inventory.html', items=items)



@app.route('/billing', methods=['GET', 'POST'])
def billing():
    items = read_csv(CSV_FILE)
    cart = []
    total = 0

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        for item in items:
            if item['id'] == product_id:
                price = float(item['price']) * quantity
                cart.append((item['name'], quantity, price))
                total += price
                break

    return render_template('billing.html', items=items, cart=cart, total=total)


@app.route('/delete/<item_id>')
def delete_item(item_id):
    data = read_csv(CSV_FILE)
    data = [item for item in data if item['id'] != item_id]
    write_csv(CSV_FILE, data)
    return redirect(url_for('inventory'))


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_text = request.form['feedback']
        sentiment = analyze_feedback(feedback_text)
        return render_template('feedback.html', sentiment=sentiment)
    return render_template('feedback.html', sentiment=None)


@app.route('/dashboard')
def dashboard():
    items = read_csv(CSV_FILE)
    sales_data = read_csv(SALES_FILE)
    feedback_data = read_csv(FEEDBACK_FILE)

    # AI Integration
    suggestions = recommend_products(items) or {}
    stockout_predictions = predict_stockout(items) or []
    sales_forecast = predict_sales(items) or []

    return render_template('dashboard.html',
                           items=items,
                           sales_data=sales_data,
                           feedback_data=feedback_data,
                           suggestions=suggestions,
                           stockout_predictions=stockout_predictions,
                           sales_forecast=sales_forecast)



if __name__ == '__main__':
    app.run(debug=True)
