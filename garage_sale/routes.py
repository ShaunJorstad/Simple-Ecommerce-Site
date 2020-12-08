import os
import string, random
import uuid
import re
from datetime import datetime, timedelta

import stripe
from flask import json, session, redirect, url_for, render_template, request, flash, jsonify

from garage_sale import app, user_image_dir, product_image_dir
from garage_sale.data_structures import get_product_from_database
from garage_sale.database import database
from garage_sale.forms import LoginForm, RegistrationForm, CreateProductForm, SettingsForm, RecoverPasswordForm
from garage_sale.security import hash_password, pep
from garage_sale.utils import logout_helper, login_required, authenticate
from garage_sale.mail import mailer


def getUser():
    uid = session.get("uid", None)
    exp = session.get("expires", None)

    if uid is None or exp is None or exp > (datetime.now() + timedelta(hours=1)):
        return None

    db = database()
    usr = db.cursor().execute('''
        SELECT fname, lname, email FROM users WHERE uid=?
    ''', (uid,)).fetchone()
    return usr


@app.route('/')
def home():
    return render_template("home.j2", user=getUser())


@app.route("/logout/")
def logout():
    logout_helper()
    return redirect(url_for("home"))

@app.route("/fetchproducts/<int:prod_id>")
def getNextProds(prod_id):
    db = database()
    c = db.cursor()

    allProducts = c.execute(f"SELECT * FROM Products WHERE id > {prod_id} ORDER by id ASC").fetchall()
    #just grab the first 20 products
    products = []
    try:
        for i in range(20):
            products.append(allProducts[i])
    except:
        products = allProducts
    
    return jsonify(products)

@app.route('/products', methods=['GET', 'POST'])
def product_list():
    uid = session.get("uid", None)

    db = database()
    c = db.cursor()

    tags = c.execute("""
        SELECT tags FROM Products
    """).fetchmany(20)

    tag_set = set()

    for tag_list in tags:
        tag_set = tag_set.union(set(map(str.strip, tag_list[0].split(","))))

    if request.method == 'POST':
        value = request.form.get("value")
        if value:
            products = c.execute('''
            SELECT * FROM Products WHERE name LIKE '%''' + value + '''%';
            ''').fetchall()
            return render_template("products.j2", products=products, user=getUser(), tags=list(tag_set))

    if uid is None:
        allProducts = c.execute("SELECT * FROM Products ORDER by id ASC").fetchall()
        #just grab the first 20 products
        products = []
        try:
            for i in range(20):
                products.append(allProducts[i])
        except:
            products = allProducts
    else:
        products = c.execute("SELECT * FROM Products WHERE user = ?", (uid,)).fetchall()

    return render_template("products.j2", products=products, user=getUser(), tags=list(tag_set))


@app.route('/products/<string:tag>')
def product_list_filtered(tag):
    db = database()
    cursor = db.cursor()

    tags = cursor.execute("""
        SELECT tags FROM Products
    """).fetchmany(20)

    tag_set = set()

    for tag_list in tags:
        tag_set = tag_set.union(set(map(str.strip, tag_list[0].split(","))))

    products = cursor.execute('''
        SELECT * FROM Products WHERE tags LIKE '%''' + tag + '''%';
        ''').fetchall()

    return render_template("products.j2", products=products, user=getUser(), tags=list(tag_set))


@app.route("/edit/product/<int:product_id>", methods=['GET'])
def edit_product_get(product_id):
    form = CreateProductForm()

    previous_product = get_product_from_database(product_id)

    form.from_product(previous_product)

    return render_template(
        "create_product.j2",
        form=form,
        edit=True,
        editing_image_file=previous_product.image_file,
        user=getUser()
    )


@app.route("/edit/product/<int:product_id>", methods=['POST'])
def edit_product_post(product_id):
    form = CreateProductForm()

    print("submitted" + str(product_id))
    print(form.posting_title.data)

    if form.validate_on_submit():
        old_product = get_product_from_database(product_id)
        new_product = form.to_product(session.get("uid", None))

        # Replace image if needed
        if new_product.image_file:
            os.remove(os.path.join(product_image_dir, old_product.image_file))

            _, extension = os.path.splitext(form.image_file.data.filename)
            image_file_name = str(uuid.uuid1()) + extension

            form.image_file.data.save(os.path.join(product_image_dir, image_file_name))
            new_product.set_image_name(image_file_name)
        else:
            new_product.set_image_name(old_product.image_file)

        new_product.tags = new_product.tags.lower()

        new_product.update_database(product_id)
        return redirect(url_for('product_list'))
    else:
        print(form.errors)
        flash("Invalid. Please try again.")
        return redirect(url_for('edit_product_get', product_id=product_id))


@app.route("/product/remove/<int:product_id>")
def remove_product(product_id):
    db = database()
    cursor = db.cursor()

    # Remove product image
    image_file = cursor.execute("""
        SELECT image_file FROM Products WHERE id = ?
    """, (product_id,)).fetchone()

    os.remove(os.path.join(product_image_dir, image_file[0]))

    # Remove product from database
    cursor.execute("""
        DELETE FROM Products WHERE id = ?
    """, (product_id,))
    db.commit()

    return redirect(url_for("product_list"))


@app.route('/products/<int:product_id>')
def product(product_id):
    conn = database()  #
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
        sellerName = sfName + " " + slName
        return render_template("product.j2", user=getUser(), id=id, name=name, description=description, price=price,
                               tags=tags,
                               image_file=image_file, condition=condition, userID=user, sName=sellerName, sEmail=sEmail,
                               sPath=sEmail + sExt)


@app.route('/checkout')
@login_required
def checkout():
    return "this is the checkout page"


@app.route('/sell', methods=['GET'])
@login_required
def sell_get():
    return render_template("create_product.j2", form=CreateProductForm(), user=getUser())


@app.route('/sell', methods=['POST'])
@login_required
def sell_post():
    sell_form = CreateProductForm()

    if sell_form.validate_on_submit():
        print(sell_form.image_file.data)
        _, extension = os.path.splitext(sell_form.image_file.data.filename)
        image_file_name = str(uuid.uuid1()) + extension

        sell_form.image_file.data.save(os.path.join(product_image_dir, image_file_name))

        new_product = sell_form.to_product(session.get("uid", None))
        new_product.set_image_name(image_file_name)

        new_product.tags = new_product.tags.lower()

        new_product.add_to_database()
        return redirect(url_for('product_list'))
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
        uid = session.get("uid", None)
        if uid != None:
            return redirect(url_for('home'))
        else:
            flash('invalid login credentials')
            return render_template('login.j2', form=form)
    else:
        flash("Invalid credentials")
        return render_template('login.j2', form=form)


@app.route('/register', methods=['GET'])
def register_get():
    return render_template('register.j2', form=RegistrationForm(), user=getUser())


@app.route('/register', methods=['POST'])
def register_post():
    form = RegistrationForm()

    if form.validate_on_submit():
        _, extension = os.path.splitext(form.profile_image.data.filename)
        form.profile_image.data.save(os.path.join(user_image_dir, str(form.email.data) + extension))

        mailSvr = mailer()
        mailSvr.sendMail(form.email.data, "Welcome to Garage Sale!",
                         "Thank you for signing up to sell items on our platform. If you did not sign up for this account please reply directly to this email stating such.")

        if form.to_user().add_to_database(extension):
            return redirect(url_for('home'))
    else:
        flash("Invalid. Please try again.")
        return render_template('register.j2', form=form, user=getUser())


@app.route('/contact', methods=["GET"])
def contact():
    return render_template("feedback.j2", user=getUser())


@app.route('/contact', methods=["POST"])
def contactEmail():
    email = request.form.get("email").lower()
    subject = request.form.get("subject")
    complaint = request.form.get("complaint")
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

    if(not re.search(regex, email)):
        flash("Invalid Email")
        return redirect(url_for('contact'))
    

    sub = f"Customer feedback about {subject}"

    print(email)
    print(subject)
    print(complaint)

    mailSvr = mailer()
    mailSvr.sendMail(email, sub, complaint)

    return redirect(url_for('home'))


@app.route('/terms')
def terms():
    return render_template("terms.j2", user=getUser())


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

        conn = database()
        cursor = conn.cursor()
        row = cursor.execute(''' 
            SELECT profileExt FROM Users where uid=? 
        ''', (uid,)).fetchone()
        oldExt = row[0]

        if form.profile_image.data is not None:
            _, extension = os.path.splitext(form.profile_image.data.filename)
            form.profile_image.data.save(os.path.join(user_image_dir, str(form.email.data) + extension))
            conn = database()
            c = conn.cursor()
            c.execute('''
                UPDATE Users
                SET profileExt = ? 
                where uid=?
            ''', (extension, uid))
            conn.commit()
        else:
            old_profile = os.path.join(user_image_dir, str(usr[2])) + oldExt
            new_profile = os.path.join(user_image_dir, form.email.data) + oldExt
            os.rename(r'' + old_profile, r'' + new_profile)

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
    # Moving forward code
    userId = session.get('uid', None)
    if userId is None:
        flash("Must be signed in to delete account")
        return redirect(url_for('home'))

    db = database()
    db.cursor().execute(''' 
        DELETE FROM Users WHERE uid=?;
    ''', (userId,))
    db.commit()
    session["uid"] = None
    session["expires"] = None
    flash("Account deleted")
    return redirect(url_for('home'))


@app.route("/recoverPassword", methods=['GET'])
def recoverPassword_get():
    return render_template('recoverPassword.j2', form=RecoverPasswordForm())


@app.route("/recoverPassword", methods=['POST'])
def recoverPassword_post():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        plainText = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(15))
        hash = hash_password(plainText, pep)
        conn = database()
        conn.cursor().execute(''' 
            UPDATE Users set hash=? where email=?;
        ''', (hash, form.email.data))
        conn.commit()

        # email password
        mailSvr = mailer()
        mailSvr.sendMail(form.email.data, 'Reset Password',
                         'Your password has been reset. Please login with the new temporary password: ' + plainText + ' and change it immediately')
        return redirect(url_for('login_get'))
    return render_template('recoverPassword.j2')


stripe.api_key = 'sk_test_51HtJ0uDZJqO6LNTXtqYjIBSHw2PLfShb1gnPC2mBbZ9QyQfFEd0O46uQJhPPoDaX21OEIltVv4UlQ63I7bW4pgHN00nE7KbjaY'


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    items = request.form
    length = int(items.get("length"))
    lineItems = []
    for i in range(length):
        print(items.get("name" + str(i)))
        lineItems.append({'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': items.get("name" + str(i)),
                'description': items.get("description" + str(i))
            },
            'unit_amount': int(float(items.get("price" + str(i))) * 100.0),
        },
            'quantity': 1,
        })
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=lineItems,
        mode='payment',
        success_url='http://127.0.0.1:5000/',
        cancel_url='http://127.0.0.1:5000/',
    )
    return jsonify(id=session.id)
