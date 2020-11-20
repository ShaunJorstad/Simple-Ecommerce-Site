from datetime import datetime

from flask import session

from garage_sale.database import database
from garage_sale.security import hash_password, pep


class User:
    email = ""
    password = ""
    fname = ""
    lname = ""

    def __init__(self, email, password, fname="", lname=""):
        self.email = email  #
        self.password = password
        self.fname = fname
        self.lname = lname

    def add_to_database(self):
        """Adds this user to the database"""
        pw_hash = hash_password(self.password, pep)

        conn = database()
        c = conn.cursor()
        c.execute('''
            INSERT into Users (email, hash, fname, lname)
            VALUES (?,?,?,?);
        ''', (self.email, pw_hash, self.fname, self.lname))
        uid = c.lastrowid
        conn.commit()

        session["uid"] = uid
        session["expires"] = datetime.now()

        return True


class Product:
    pass
