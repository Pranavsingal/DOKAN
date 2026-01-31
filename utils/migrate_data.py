import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Product, TransactionItem, SalesRecord, Feedback

def migrate():
    with app.app_context():
        db.create_all()
        print("✅ Database tables checked/created.")

        # 1. Migrate Inventory
        if os.path.exists('data/inventory.csv'):
            df = pd.read_csv('data/inventory.csv')
            for _, row in df.iterrows():
                # Use db.session.get() instead of .query.get() to fix LegacyWarning
                if not db.session.get(Product, row['id']):
                    product = Product(
                        id=row['id'],
                        name=row['name'],
                        category=row['category'],
                        stock=row['stock'],
                        price=row['price'],
                        expiry_date=str(row.get('expiry_date', '')),
                        supplier=str(row.get('supplier', ''))
                    )
                    db.session.add(product)
            print("✅ Inventory migrated.")

        # 2. Migrate Transactions
        if os.path.exists('data/transactions.csv'):
            df = pd.read_csv('data/transactions.csv')
            for _, row in df.iterrows():
                # Check for duplicates (optional but good for re-running)
                # Since TransactionItem has no unique ID in CSV, we just add them
                # A smarter check would be complex, but for migration, this is fine
                trans = TransactionItem(
                    transaction_id=int(row['transaction_id']),
                    item_id=int(row['item_id'])
                )
                db.session.add(trans)
            print("✅ Transactions migrated.")

        # 3. Migrate Sales
        if os.path.exists('data/sales.csv'):
            df = pd.read_csv('data/sales.csv')
            for _, row in df.iterrows():
                sale = SalesRecord(
                    item_id=int(row['item_id']),
                    date=str(row['date']),
                    sales=float(row['sales'])
                )
                db.session.add(sale)
            print("✅ Sales records migrated.")

        # 4. Migrate Feedback (Fixed Parser Error)
        if os.path.exists('data/feedback.csv'):
            try:
                # on_bad_lines='skip' will ignore rows with extra commas
                df = pd.read_csv('data/feedback.csv', on_bad_lines='skip')
                for _, row in df.iterrows():
                    if not db.session.get(Feedback, row['feedback_id']):
                        fb = Feedback(
                            id=row['feedback_id'],
                            text=str(row['feedback_text'])
                        )
                        db.session.add(fb)
                print("✅ Feedback migrated.")
            except Exception as e:
                print(f"⚠️ skipped feedback due to error: {e}")

        db.session.commit()
        print("🚀 Migration Complete! Data saved to instance/dokan.db")

if __name__ == "__main__":
    migrate()