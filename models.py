'''
In this file, you define the database tables as classes (Account, Product, Transaction).
The columns of the classes correspond to the columns of the tables.
However, this file does not create the database, it only defines the structure of the tables


his code defines three database models: Account, Product, and Transaction.
These models correspond to tables in the database, and each class defines the table's columns and their data types.
The __repr__ method provides a way to represent each object as a string when printed, which is useful for debugging and logging.
'''
from db import db  # Import from db.py

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<Account balance={self.balance}>"

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), unique=True, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Product {self.product_name}, price={self.unit_price}, stock={self.stock_quantity}>"

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'Sale', 'Add', 'Subtract'
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    new_balance = db.Column(db.Float, nullable=False)
    product = db.Column(db.String(100), nullable=True)  # Product name for sales
    cost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.type}, amount={self.amount}, new_balance={self.new_balance}>"
