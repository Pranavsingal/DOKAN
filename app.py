from flask import Flask, render_template, request, redirect, url_for
import csv
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

CSV_FILE = 'data/inventory.csv'

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
    return "Billing Placeholder"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)