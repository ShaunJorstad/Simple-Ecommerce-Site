import os
import stripe
from datetime import datetime, timedelta

from flask import session, redirect, url_for, render_template, request, flash, jsonify

from garage_sale import app, image_dir
from garage_sale.database import database
from garage_sale.forms import LoginForm, RegistrationForm, CreateProductForm, SettingsForm
from garage_sale.utils import logout_helper, login_required, authenticate
from garage_sale.security import hash_password, pep


@app.route('/')
def home():
    uid = session.get("uid", None)
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
    db = database()
    c = db.cursor()

    pList = c.execute("SELECT * FROM Products").fetchall()

    return render_template("products.j2", products = pList)


@app.route('/products/<int:product_id>')
def product(product_id):
    conn = database()#
    c = conn.cursor()
    result = c.execute('''
        SELECT id, name, description, price, tags, image_file, condition, user, U.fname, U.lname, U.email, U.profileExt FROM Products
        JOIN Users U ON Products.user = U.uid
        WHERE id=?;  
    ''', (product_id,)).fetchall()
    if len(result) == 0:
        return render_template("products.j2")
    for row in result:
        id = row[0]
        name = row[1]
        description = row[2]
        price = row[3]
        tags = row[4].split(', ')
        image_file = row[5]
        condition = row[6]
        user = row[7]
        sfName = row[8]
        slName = row[9] 
        sEmail = row[10]
        sExt = row[11]
        imagePath = os.path.join('images/products', image_file)
        sellerPath = os.path.join('images/users', sEmail + "." + sExt)
        sellerName = sfName + " " + slName

        return render_template("product.j2", id=id, name=name, description=description, price=price, tags=tags, image_file=imagePath, condition=condition, userID=user, sName=sellerName, sEmail=sEmail, sPath=sellerPath)



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
    sell_form = CreateProductForm()

    if sell_form.validate_on_submit():
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
        if session["uid"] != None:
            return redirect(url_for('home'))
        else: 
            flash('invalid login credentials')
            return render_template('login.j2', form=form)
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

        if form.to_user().add_to_database(extension):
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

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    uid = session.get("uid")
    form = SettingsForm()

    conn = database()
    usr = conn.cursor().execute('''
        SELECT fname, lname, email FROM users WHERE uid=?
    ''', (uid,)).fetchone()

    if form.validate_on_submit() and request.method == 'POST':
        # _, extension = os.path.splitext(form.profile_image.data.filename)
        # form.profile_image.data.save(os.path.join(image_dir, str(form.email.data) + extension))
        if form.password.data != '' and form.password.data != form.confirm.data:
            flash("passwords must match")
        elif form.password.data != '':
            pw_hash = hash_password(form.password.data, pep)
            conn.cursor().execute(''' 
                UPDATE Users 
                SET hash=?, email=?, fname=?, lname=?
                WHERE uid=?
            ''', (pw_hash, form.email.data, form.fname.data, form.lname.data, uid))
            conn.commit()
        else:
            # update other info
            conn.cursor().execute(''' 
                UPDATE Users 
                SET email=?, fname=?, lname=?
                WHERE uid=?
            ''', (form.email.data, form.fname.data, form.lname.data, uid))
            conn.commit()

        if form.profile_image.data is not None:
            _, extension = os.path.splitext(form.profile_image.data.filename)
            form.profile_image.data.save(os.path.join(image_dir, str(form.email.data) + extension))
        else:
            old_profile = os.path.join(image_dir, str(usr[2])) + '.jpg'
            new_profile = os.path.join(image_dir, form.email.data) + '.jpg'
            os.rename(r''+old_profile ,r''+new_profile)

        flash("Settings have been updated")
        form.accept_changes.data = False
        return render_template('settings.j2', user=usr, form=form)
    elif request.method == 'POST':
        flash("Invalid Fields. Please try again.")
        return render_template('settings.j2', user=usr, form=form)
    elif request.method == 'GET':
        form.fname.data = usr[0]
        form.lname.data = usr[1]
        form.email.data = usr[2]
    return render_template('settings.j2', user=usr, form=form)

@app.route("/deleteAccount/", methods=['POST'])
def move_forward():
    #Moving forward code
    userId = session.get('uid')
    db = database() 
    db.cursor().execute(''' 
        DELETE FROM Users WHERE uid=?;
    ''', (userId,))
    db.commit()
    session["uid"] = None
    session["expires"] = None
    flash("Account deleted")
    return redirect(url_for('home'))


stripe.api_key = 'sk_test_51HtJ0uDZJqO6LNTXtqYjIBSHw2PLfShb1gnPC2mBbZ9QyQfFEd0O46uQJhPPoDaX21OEIltVv4UlQ63I7bW4pgHN00nE7KbjaY'

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    items = request.form
    length = int(items.get("length"))
    lineItems = []
    for i in range(length):
        lineItems.append({'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': items.get("name" + str(i)),
                'description': items.get("description" + str(i))
            },
            'unit_amount': int(items.get("price" + str(i))) * 100,
        },
        'quantity': 1,
        })
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items= lineItems,
        mode='payment',
        success_url= 'http://127.0.0.1:5000/',
        cancel_url= 'http://127.0.0.1:5000/',
    )
    return jsonify(id=session.id)

'''[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
            'name': 'T-shirt',
            },
            'unit_amount': 5000,
        },
        'quantity': 1,
        },
        {
        'price_data': {
            'currency': 'usd',
            'product_data': {
            'name': 'T-shirt 2',
            },
            'unit_amount': 6000,
        },
        'quantity': 1,
        }]'''