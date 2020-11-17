from flask import *

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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

@app.route('/login')
def login():
    return "this is the login page"

@app.route('/signup')
def signup():
    return "this is the signup page"

@app.route('/contact')
def contact():
    return "this is the contact us page"

@app.route('/terms')
def terms():
    return "this is the terms page"