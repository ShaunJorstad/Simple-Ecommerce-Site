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


def get_product_from_database(product_id):
    conn = database()
    c = conn.cursor()

    product_info = c.execute("""
        SELECT * FROM Products WHERE id = ?
    """, (product_id,)).fetchone()

    return Product(
        product_info[1],
        product_info[2],
        product_info[7],
        product_info[3],
        product_info[4],
        product_info[5],
        product_info[6]
    )


class Product:
    def __init__(self, name, price, user, description="", tags="", image_file="", condition=""):
        self.name = name
        self.price = price
        self.description = description
        self.tags = tags
        self.image_file = image_file
        self.condition = condition
        self.user = user

    def set_image_name(self, image_name):
        self.image_file = image_name

    def add_to_database(self):
        conn = database()
        c = conn.cursor()
        c.execute('''
            INSERT into Products (name, price, description, tags, image_file, condition, user)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        ''', (self.name, self.price, self.description, self.tags, self.image_file, self.condition, self.user))
        conn.commit()

    def update_database(self, product_id):
        conn = database()
        c = conn.cursor()

        product_info = c.execute("""
            SELECT * FROM Products WHERE id = ?
        """, (product_id,)).fetchone()

        if product_info is None:
            return

        c.execute("""
            UPDATE Products SET
                name = ?,
                price = ?,
                description = ?,
                tags = ?,
                image_file = ?,
                condition = ?
            WHERE id = ?
        """, (self.name, self.price, self.description, self.tags, self.image_file, self.condition, product_id))
        conn.commit()
