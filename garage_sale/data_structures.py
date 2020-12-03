from datetime import datetime

from flask import session

from garage_sale.database import database
from garage_sale.security import hash_password, pep


class User:
    def __init__(self, email, password, fname="", lname=""):
        self.email = email  #
        self.password = password
        self.fname = fname
        self.lname = lname

    def add_to_database(self, extension=""):
        """Adds this user to the database"""
        pw_hash = hash_password(self.password, pep)

        conn = database()
        c = conn.cursor()
        c.execute('''
            INSERT into Users (email, hash, fname, lname, profileExt)
            VALUES (?,?,?,?, ?);
        ''', (self.email, pw_hash, self.fname, self.lname, extension))
        uid = c.lastrowid
        conn.commit()

        session["uid"] = uid
        session["expires"] = datetime.now()

        return True


class Product:
    def __init__(self, name, price, description="", tags="", image_file="", condition=""):
        self.name = name
        self.price = price
        self.description = description
        self.tags = tags
        self.image_file = image_file
        self.condition = condition

    def set_image_name(self, image_name):
        self.image_file = image_name

    def add_to_database(self):
        conn = database()
        c = conn.cursor()
        c.execute('''
            INSERT into Products (name, price, description, tags, image_file, condition)
            VALUES (?, ?, ?, ?, ?, ?);
        ''', (self.name, self.price, self.description, self.tags, self.image_file, self.condition))
        conn.commit()
