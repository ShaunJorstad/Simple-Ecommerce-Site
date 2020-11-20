import os
from datetime import datetime, timedelta

from flask import session, redirect, url_for, render_template, request, flash
from werkzeug.datastructures import CombinedMultiDict

from garage_sale import app, image_dir
from garage_sale.data_structures import User
from garage_sale.database import database
from garage_sale.forms import LoginForm, RegistrationForm
from garage_sale.utils import logout_helper, login_required, authenticate


@app.route('/')
def home():
    uid = session.get("uid")
    exp = session.get("expires", None)

    if uid is None or exp is None or exp > (datetime.now() + timedelta(hours=1)):
        return render_template("home.j2", user=None)
    else:
        db = database()
        usr = db.cursor().execute('''
            SELECT fname, lname, email FROM users WHERE uid=?
        ''', (uid,)).fetchone()
        return render_template("home.j2", user=usr)


@app.route("/logout/")
def logout():
    logout_helper()
    return redirect(url_for("home"))


@app.route('/products/<int:product_id>')
@login_required
def products(product_id):
    return render_template("products.html")


@app.route('/checkout')
@login_required
def checkout():
    return "this is the checkout page"


@app.route('/sell')
@login_required
def sell():
    return "this is the page to sell an item"


@app.route('/login', methods=['GET', 'POST'])
def login():
    # form = RegistrationForm(request.form)
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.email.data, form.password.data)
        authenticate(user)
        return redirect(url_for('home'))
    form = LoginForm()
    return render_template('login.j2', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        profile = request.files['profile']
        filetype = profile.filename.split('.')[1]
        print(filetype)
        if not (filetype == "jpg" or filetype == "png"):
            flash("profile must be jpg or png")
            return redirect(url_for('register'))
        profile.save(os.path.join(image_dir, str(form.email.data) + '.' + str(filetype)))
        user = User(form.email.data, form.password.data, form.fname.data, form.lname.data)
        if user.add_to_database():
            return redirect(url_for('home'))

    form = RegistrationForm()
    return render_template('register.j2', form=form)


@app.route('/contact')
@login_required
def contact():
    return render_template("feedback.html")


@app.route('/terms')
def terms():
    uid = session.get("uid")
    exp = session.get("expires", None)

    if uid is None or exp is None or exp > (datetime.now() + timedelta(hours=1)):
        return render_template("terms.j2", user=None)
    else:
        db = database()
        usr = db.cursor().execute('''
            SELECT fname, lname, email FROM users WHERE uid=?
        ''', (uid,)).fetchone()
        return render_template("terms.j2", user=usr)
