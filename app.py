from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

CSV_FILE = 'data/inventory.csv'
TRANSACTIONS_FILE = 'data/transactions.csv'

# --- 1. Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helper Functions ---
def read_csv(file_path):
    try:
        with open(file_path, mode='r', newline='') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        return []

def write_csv(file_path, data):
    if not data:
        return
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "User already exists! <a href='/register'>Try again</a>"
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
            return redirect(url_for('inventory'))
        return "Invalid credentials! <a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    items = read_csv(CSV_FILE)

    if request.method == 'POST':
        # Validation Logic
        try:
            stock = int(request.form['stock'])
            price = float(request.form['price'])
            if stock < 0 or price < 0:
                return "Error: Stock and Price cannot be negative! <a href='/inventory'>Go Back</a>"
        except ValueError:
            return "Error: Invalid number format!"

        item = {
            'id': request.form['id'],
            'name': request.form['name'],
            'category': request.form['category'],
            'stock': stock,
            'price': price,
            'expiry_date': request.form['expiry_date'],
            'supplier': request.form['supplier']
        }

        # Edit/Update Logic
        data = read_csv(CSV_FILE)
        for i, row in enumerate(data):
            if row['id'] == item['id']:
                data[i] = item  # Update existing
                break
        else:
            data.append(item)   # Add new
        
        write_csv(CSV_FILE, data)
        return redirect(url_for('inventory'))

    # Render with empty edit_item for normal view
    return render_template('inventory.html', items=items, edit_item=None)

@app.route('/edit_product/<item_id>')
@login_required
def edit_product(item_id):
    items = read_csv(CSV_FILE)
    item_to_edit = next((item for item in items if item['id'] == item_id), None)
    return render_template('inventory.html', items=items, edit_item=item_to_edit)

@app.route('/delete/<item_id>')
@login_required
def delete_item(item_id):
    data = read_csv(CSV_FILE)
    data = [item for item in data if item['id'] != item_id]
    write_csv(CSV_FILE, data)
    return redirect(url_for('inventory'))

@app.route('/dashboard')
@login_required
def dashboard():
    return "Dashboard Placeholder"  # Simplified for now

@app.route('/billing')
@login_required
def billing():
    return render_template('billing.html')


@app.route('/api/inventory')
@login_required
def api_inventory():
    """API endpoint to get inventory data for billing page"""
    items = read_csv(CSV_FILE)
    return jsonify(items)


@app.route('/api/checkout', methods=['POST'])
@login_required
def api_checkout():
    """
    API endpoint to process checkout:
    - Updates inventory.csv (decreases stock)
    - Logs sale in transactions.csv
    """
    try:
        data = request.get_json()
        items = data.get('items', [])
        customer_name = data.get('customer_name', 'Unknown')
        
        if not items:
            return jsonify({'success': False, 'error': 'No items in cart'}), 400
        
        # Read current inventory
        inventory = read_csv(CSV_FILE)
        
        # Validate stock availability first
        for cart_item in items:
            item_id = str(cart_item.get('id'))
            qty = int(cart_item.get('qty', 0))
            
            inv_item = next((i for i in inventory if str(i['id']) == item_id), None)
            if not inv_item:
                return jsonify({'success': False, 'error': f'Item ID {item_id} not found'}), 400
            
            if int(inv_item['stock']) < qty:
                return jsonify({'success': False, 'error': f'Not enough stock for {inv_item["name"]}'}), 400
        
        # Generate new transaction ID
        transactions = read_csv(TRANSACTIONS_FILE)
        if transactions:
            max_trans_id = max(int(t['transaction_id']) for t in transactions)
            new_trans_id = max_trans_id + 1
        else:
            new_trans_id = 1
        
        # Update inventory and create transaction records
        new_transactions = []
        for cart_item in items:
            item_id = str(cart_item.get('id'))
            qty = int(cart_item.get('qty', 0))
            
            # Update inventory stock
            for inv_item in inventory:
                if str(inv_item['id']) == item_id:
                    inv_item['stock'] = int(inv_item['stock']) - qty
                    break
            
            # Add transaction record (one per item in the bill)
            new_transactions.append({
                'transaction_id': new_trans_id,
                'item_id': item_id
            })
        
        # Write updated inventory
        write_csv(CSV_FILE, inventory)
        
        # Append new transactions
        transactions.extend(new_transactions)
        write_csv(TRANSACTIONS_FILE, transactions)
        
        return jsonify({
            'success': True, 
            'message': 'Checkout successful',
            'transaction_id': new_trans_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)