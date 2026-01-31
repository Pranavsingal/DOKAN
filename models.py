from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# 1. User Model (Keep as is)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# 2. Product Model (Matches inventory.csv)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Matches 'id'
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0) # Matches 'stock'
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.String(20)) # Matches 'expiry_date'
    supplier = db.Column(db.String(100)) # Matches 'supplier'

# 3. Transaction Model (Matches transactions.csv)
# This table links items to a transaction ID (Many-to-Many relationship)
class TransactionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, nullable=False) # Matches 'transaction_id'
    item_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) # Matches 'item_id'

# 4. Sales Record (Matches sales.csv)
class SalesRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) # Matches 'item_id'
    date = db.Column(db.String(20), nullable=False) # Matches 'date'
    sales = db.Column(db.Integer, nullable=False) # Matches 'sales'

# 5. Feedback Model (Matches feedback.csv)
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Matches 'feedback_id'
    text = db.Column(db.Text, nullable=False) # Matches 'feedback_text'