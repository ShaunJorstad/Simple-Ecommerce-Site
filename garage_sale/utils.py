from datetime import datetime, timedelta
from functools import wraps

from flask import session, redirect, url_for

from garage_sale.database import database
from garage_sale.security import check_password, pep


def authenticate(user):
    """ authenticates attempted login"""
    # checks if user exists in database
    c = database()  #
    result_hash = c.cursor().execute(''' 
        Select hash, uid from Users  
        where email=?
    ''', (user.email,)).fetchone()
    if result_hash is None:
        return redirect(url_for('login'))
    elif check_password(user.password, result_hash[0], pep):
        session["uid"] = result_hash[1]
        session["expires"] = datetime.now()


def logout_helper():
    """Logout user in current session"""
    session["uid"] = None


def login_required(f):
    """Ensures the decorated function requires a login"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        # check that session has a uid that is still good
        uid = session.get("uid")
        exp = session.get("expires", None)

        # if uid or exp is missing or exp has passed . . .
        if uid is None or exp is None or exp > (datetime.now() + timedelta(hours=1)):
            return redirect(url_for("login_get"))

        # only if the user is logged in should the route handler run
        return f(*args, **kwargs)

    return wrapper
