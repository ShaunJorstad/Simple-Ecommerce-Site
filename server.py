from flask import *
from dataStructures import *
import os, sqlite3

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# DATABASE MANAGEMENT ----------------------------------------------------------------
DATABASE = '/path/to/databaseFile'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def db_add(user):
    '''add's the user to the database'''
    pass



# ROUTES ----------------------------------------------------------------
@app.route('/')
def home():
    return "this is the home page"

@app.route('/products/<int:productID>')
def products(productID):
    return render_template("products.html")

@app.route('/checkout')
def checkout():
    return "this is the checkout page"

@app.route('/sell')
def sell():
    return "this is the page to sell an item"

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.email.data, form.password.data)
    return "this is the login page"

@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.email.data, form.password.data)
        db_add(user)
    return "this is the signup page"

@app.route('/contact')
def contact():
    return "this is the contact us page"

@app.route('/terms')
def terms():
    return "this is the terms page"