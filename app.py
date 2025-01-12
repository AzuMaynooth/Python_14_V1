'''

This file handles the creation of the tables in the database. The database is created automatically when you run the Flask application,
 thanks to the db.create_all() function, which creates the tables defined in models.py if they do not already exist.
'''

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
from models import Product, Account, Transaction
from db import db  # Make sure to use the db instance from db.py

#Create flas application
app = Flask(__name__)

# get the absolute path y
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# get the absolute path to DB
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database", "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  Required for flash messages

# Initialize the database with the app.
db.init_app(app)

# Create the tables if they do not exist when starting the application
first_request = True
@app.before_request
def create_tables():
    db.create_all()  # Create the tables in the database

    # Add initial balance if it does not exist
    if not Account.query.first():
        db.session.add(Account(balance=1000.0))
        db.session.commit()
@app.route('/')
def index():
    account = Account.query.first()
    balance = account.balance if account else 0.0
    inventory = Product.query.all()
    operation_history = Transaction.query.order_by(Transaction.date.desc()).all()

    return render_template(
        'index.html',
        balance=balance,
        inventory=inventory,
        operation_history=operation_history
    )


@app.route('/purchase-form', methods=["GET", "POST"])
def purchase_form():
    if request.method == "POST":
        product_name = request.form['product_name']
        unit_price = request.form['unit_price']
        number_of_pieces = request.form['number_of_pieces']

        # Validar si la cantidad no está vacía
        if not number_of_pieces:
            flash('Quantity is required for purchase transactions.', 'error')
            return redirect(url_for('purchase_form'))

        if not product_name or not unit_price or not number_of_pieces:
            flash('Please complete all fields.', 'error')
            return redirect(url_for('purchase_form'))

        try:
            unit_price = round(float(unit_price), 2)
            number_of_pieces = int(number_of_pieces)

            if unit_price <= 0 or number_of_pieces <= 0:
                flash('The unit price and quantity must be greater than zero.', 'error')
                return redirect(url_for('purchase_form'))
        except ValueError:
            flash('Please enter correct values for price and quantity.', 'error')
            return redirect(url_for('purchase_form'))

        total_cost = round(unit_price * number_of_pieces, 2)
        account = Account.query.first()

        if account.balance >= total_cost:
            account.balance -= total_cost  # Restar el costo total
            db.session.commit()

            # Revisar si el producto ya existe
            product = Product.query.filter_by(product_name=product_name).first()
            if product:
                total_existing_value = product.unit_price * product.stock_quantity
                total_new_value = unit_price * number_of_pieces
                new_stock_quantity = product.stock_quantity + number_of_pieces
                product.unit_price = round((total_existing_value + total_new_value) / new_stock_quantity, 2)
                product.stock_quantity = new_stock_quantity
            else:
                new_product = Product(
                    product_name=product_name,
                    unit_price=unit_price,
                    stock_quantity=number_of_pieces
                )
                db.session.add(new_product)

            # Crear una transacción de compra
            transaction = Transaction(
                type='Purchase',
                date=datetime.datetime.now(),
                amount=total_cost,
                new_balance=account.balance,
                product=product_name,
                cost=total_cost
            )
            db.session.add(transaction)
            db.session.commit()

            flash(f'Successful purchase! Product: {product_name}, Total: {total_cost:.2f}€', 'success')
        else:
            flash('You do not have enough balance to make the purchase.', 'error')

    # Recuperar el inventario y saldo de la cuenta
    inventory = Product.query.all()
    account = Account.query.first()
    return render_template('purchase-form.html', balance=round(account.balance, 2), inventory=inventory)

# Formulario de venta
@app.route('/sale-form', methods=["GET", "POST"])
def sale_form():
    unit_price = None

    if request.method == "POST":
        product_name = request.form['product_name']
        number_of_pieces = request.form['number_of_pieces']

        # Validar si la cantidad no está vacía
        if not number_of_pieces:
            flash('Quantity is required for sale transactions.', 'error')
            return redirect(url_for('sale_form'))

        if not product_name or not number_of_pieces:
            flash('Please complete all fields.', 'error')
            return redirect(url_for('sale_form'))

        product = Product.query.filter_by(product_name=product_name).first()

        if not product:
            flash(f'The product "{product_name}" is not available.', 'error')
            return redirect(url_for('sale_form'))

        if product.stock_quantity >= int(number_of_pieces):
            product.stock_quantity -= int(number_of_pieces)
            sale_amount = product.unit_price * int(number_of_pieces)
            account = Account.query.first()
            account.balance += sale_amount
            db.session.commit()

            # Crear una transacción de venta
            transaction = Transaction(
                type='Sale',
                date=datetime.datetime.now(),
                amount=sale_amount,
                new_balance=account.balance,
                product=product_name,
                cost=sale_amount
            )
            db.session.add(transaction)
            db.session.commit()

            flash(f'Successful sale! Product: {product_name}, Total: {sale_amount:.2f}€', 'success')
        else:
            flash(f'There is not enough stock of "{product_name}" to make the sale.', 'error')

    # Recuperar el inventario y saldo de la cuenta
    inventory = Product.query.all()
    account = Account.query.first()
    return render_template('sale-form.html', balance=account.balance, inventory=inventory, unit_price=unit_price)

# Cambiar balance
@app.route('/balance-change-form', methods=["GET", "POST"])
def balance_change_form():
    if request.method == "POST":
        operation_type = request.form['operation_type']
        change_value = request.form['change_value']

        if not operation_type or not change_value:
            flash('Please complete all fields.', 'error')
            return redirect(url_for('balance_change_form'))

        try:
            change_value = float(change_value)
        except ValueError:
            flash('Please enter a valid numerical value for the change.', 'error')
            return redirect(url_for('balance_change_form'))

        account = Account.query.first()

        if operation_type == 'add':
            account.balance += change_value
            flash(f'The balance has been increased by {change_value:.2f}€! New balance: {account.balance:.2f}€', 'success')

        elif operation_type == 'subtract':
            if account.balance >= change_value:
                account.balance -= change_value
                flash(f'The balance has been reduced by {change_value:.2f}€! New balance: {account.balance:.2f}€', 'success')
            else:
                flash('Insufficient balance to carry out this operation.', 'error')

        # Crear transacción para registrar el cambio
        transaction = Transaction(
            type='Add' if operation_type == 'add' else 'Subtract',
            date=datetime.datetime.now(),
            amount=change_value if operation_type == 'add' else -change_value,
            new_balance=account.balance,
            product='',
            cost=0
        )
        db.session.add(transaction)
        db.session.commit()

    account = Account.query.first()
    return render_template('balance-change-form.html', balance=account.balance)

# Historial de operaciones
@app.route('/history/', methods=['GET', 'POST'])
def history():
    start_date = None
    end_date = None
    show_table = False
    filtered_history = []

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Convertir las fechas a objetos datetime si están presentes
        try:
            if start_date:
                start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
            if end_date:
                end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

            # Filtrar las transacciones según las fechas
            query = Transaction.query
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)

            filtered_history = query.order_by(Transaction.date.desc()).all()
            show_table = bool(filtered_history)

        except ValueError:
            flash('Please enter valid date values (dd-mm-yyyy).', 'error')

    return render_template(
        'history.html',
        operation_history=filtered_history,
        start_date=start_date,
        end_date=end_date,
        show_table=show_table
    )

if __name__ == '__main__':
    app.run(debug=True)
