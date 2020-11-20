import os
import sqlite3

from garage_sale import app, make_g

DATABASE = 'database.sqlite3'
script_dir = os.path.dirname(__file__)
dbpath = os.path.join(script_dir, "../database.sqlite3")


@make_g
def database():
    """Returns an instance to the database"""
    return sqlite3.connect(DATABASE)


@app.teardown_appcontext
def close_connection(exception):
    """"Closes the open connection to the database"""
    db = database()

    if db is not None:
        db.close()
