from flask import Flask, render_template, request, redirect, url_for
import csv, os
from ai.sales_forecast import predict_sales
from ai.stockout_predictor import predict_stockout
from ai.recommender import recommend_products
from ai.categorizer import categorize_product
from ai.sentiment_analyzer import analyze_feedback
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'  # Required for Login
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
@login_required
def inventory():
    items = read_csv(CSV_FILE)

    if request.method == 'POST':
        # 1. Capture and Validate Inputs
        try:
            stock = int(request.form['stock'])
            price = float(request.form['price'])
            
            # --- THE FIX: Block negative numbers ---
            if stock < 0 or price < 0:
                return "Error: Stock and Price cannot be negative! <a href='/inventory'>Go Back</a>"
            # ---------------------------------------

        except ValueError:
            return "Error: Invalid number format! <a href='/inventory'>Go Back</a>"

        # 2. Create the item (if validation passes)
        item = {
            'id': request.form['id'],
            'name': request.form['name'],
            'category': request.form['category'],
            'stock': stock,       # Use the validated variable
            'price': price,       # Use the validated variable
            'expiry_date': request.form['expiry_date'],
            'supplier': request.form['supplier']
        }

        # 3. Save to CSV
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
@login_required
def billing():
    items = read_csv(CSV_FILE)
    cart = []
    total = 0

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        
        items = read_csv(CSV_FILE)
        
        for item in items:
            if item['id'] == product_id:
                current_stock = float(item['stock'])
                
                if current_stock >= quantity:
                   
                    price = float(item['price']) * quantity
                    item['stock'] = current_stock - quantity

                    cart.append((item['name'], quantity, price))
                    total += price

                    write_csv(CSV_FILE, items)
                else:
                    print(f"Error: Not enough stock for {item['name']}")
                
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
@login_required
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

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return "User already exists! <a href='/register'>Try again</a>"
        
        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
            
        return "Invalid credentials! <a href='/login'>Try again</a>"
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
# -----------------------------

if __name__ == '__main__':
    app.run(debug=True)

