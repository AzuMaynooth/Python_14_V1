'''
simply initializes the SQLAlchemy instance that will be used throughout the project to connect to and manage the database. It does not create the database; it only defines the connection to it.
this file does not handle the creation of the database itself. Instead, it sets up the connection and allows you to define and manipulate database tables via Python code.
The actual database creation happens when you call db.create_all() in the application (like in app.py), and the database file will be created when the application runs for the first time.
'''

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

