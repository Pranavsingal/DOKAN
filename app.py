import os
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

# --- CONFIGURATION ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Force DB to be in the current folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dokan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.String(20))
    supplier = db.Column(db.String(100))

class TransactionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class SalesRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    sales = db.Column(db.Float, nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

# --- LOGIN MANAGER ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTO-MIGRATION FUNCTION ---
def load_data_from_csv():
    """Restores products from CSV if the database is empty."""
    csv_path = os.path.join(basedir, 'data', 'inventory.csv')
    if os.path.exists(csv_path):
        # We check if the table is empty
        if Product.query.count() == 0:
            print(f"🔄 Reloading data from {csv_path}...")
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Use CSV ID if available
                        p_id = int(row['id'])
                        if not Product.query.get(p_id):
                            product = Product(
                                id=p_id,
                                name=row['name'],
                                category=row['category'],
                                stock=int(row['stock']),
                                price=float(row['price']),
                                expiry_date=row.get('expiry_date', ''),
                                supplier=row.get('supplier', '')
                            )
                            db.session.add(product)
                    except Exception:
                        pass # Skip bad rows
            db.session.commit()
            print("✅ Data restored successfully.")

# --- ROUTES ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('inventory'))
    return redirect(url_for('login'))

@app.route('/inventory')
@login_required
def inventory():
    all_products = Product.query.all()
    # FIXED: Changed 'items' to 'products' to match your HTML loop
    return render_template('inventory.html', products=all_products)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    # 1. Get Data
    name = request.form.get('name')
    category = request.form.get('category')
    stock = request.form.get('stock')
    price = request.form.get('price')
    expiry_date = request.form.get('expiry_date')
    supplier = request.form.get('supplier')

    # 2. AUTO-CALCULATE ID (Prevents "Unique Constraint" Crash)
    last_product = Product.query.order_by(Product.id.desc()).first()
    new_id = (last_product.id + 1) if last_product else 1

    # 3. Save
    new_item = Product(
        id=new_id,
        name=name,
        category=category,
        stock=int(stock) if stock else 0,
        price=float(price) if price else 0.0,
        expiry_date=expiry_date,
        supplier=supplier
    )

    try:
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
    
    return redirect(url_for('inventory'))

@app.route('/delete/<int:item_id>')
@login_required
def delete_item(item_id):
    product = Product.query.get(item_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('inventory'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                         items=[], sales_data=[], feedback_data=[], 
                         suggestions={}, stockout_predictions=[], sales_forecast=[])

@app.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        quantity = int(request.form.get('quantity'))
        product = Product.query.get(item_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            sale = SalesRecord(item_id=product.id, date=datetime.now().strftime('%Y-%m-%d'), sales=quantity * product.price)
            db.session.add(sale)
            db.session.commit()
            return redirect(url_for('inventory'))
    return render_template('billing.html')

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    return render_template('feedback.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('inventory'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('inventory'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_data_from_csv() # THIS LOADS YOUR MISSING DATA
    app.run(debug=True)