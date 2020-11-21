import os
from datetime import datetime, timedelta

from flask import session, redirect, url_for, render_template, request, flash

from garage_sale import app, image_dir
from garage_sale.database import database
from garage_sale.forms import LoginForm, RegistrationForm, CreateProductForm
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


@app.route('/products')
def product_list():
    return render_template("products.j2")


@app.route('/products/<int:product_id>')
@login_required
def product(product_id):
    return render_template("products.j2")


@app.route('/checkout')
@login_required
def checkout():
    return "this is the checkout page"


@app.route('/sell', methods=['GET'])
@login_required
def sell_get():
    return render_template("create_product.j2", form=CreateProductForm())


@app.route('/sell', methods=['POST'])
@login_required
def sell_post():
    sell_form = CreateProductForm(request.form)

    if sell_form.validate():
        sell_form.to_product().add_to_database()
        return redirect(url_for('home'))
    else:
        flash("Invalid. Please try again.")
        return redirect(url_for('sell_get'))


@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.j2', form=LoginForm())


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.to_user()
        authenticate(user)
        return redirect(url_for('home'))
    else:
        flash("Invalid credentials")
        return render_template('login.j2', form=form)


@app.route('/register', methods=['GET'])
def register_get():
    return render_template('register.j2', form=RegistrationForm())


@app.route('/register', methods=['POST'])
def register_post():
    form = RegistrationForm()

    if form.validate_on_submit():
        _, extension = os.path.splitext(form.profile_image.data.filename)
        form.profile_image.data.save(os.path.join(image_dir, str(form.email.data) + extension))

        if form.to_user().add_to_database():
            return redirect(url_for('home'))
    else:
        flash("Invalid. Please try again.")
        return render_template('register.j2', form=form)


@app.route('/contact')
def contact():
    return render_template("feedback.j2")


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
