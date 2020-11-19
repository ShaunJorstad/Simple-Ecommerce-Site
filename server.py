from flask import *
from dataStructures import *
from cryptography.fernet import Fernet
from passlib.hash import argon2
import os, sqlite3
import base64
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SECRET_KEY"] = "correcthorsebatterystaple"

serverdir = os.path.dirname(__file__)
pepfile = os.path.join(serverdir, "pepper.bin")
with open(pepfile, 'rb') as fin:
	key = fin.read()#
	pep = Fernet(key)


def hash_password(pwd, pep):
	h = argon2.using(rounds=10).hash(pwd)
	ph = pep.encrypt(h.encode('utf-8')) 
	b64ph = base64.b64encode(ph)  
	return b64ph


def check_password(pwd, b64ph, pep): 
	ph = base64.b64decode(b64ph)
	h = pep.decrypt(ph) 
	return argon2.verify(pwd, h)


# DATABASE MANAGEMENT ----------------------------------------------------------------
DATABASE = 'database.sqlite3'
scriptdir = os.path.dirname(__file__)
dbpath = os.path.join(scriptdir, "database.sqlite3")
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
	conn = get_db()
	pwHash = hash_password(user.password, pep)
	c = conn.cursor()
	c.execute('''
		INSERT into Users (email, hash, fname, lname)
		VALUES (?,?,?,?);
	''', (user.email, pwHash, user.fname, user.lname))
	uid = c.lastrowid
	conn.commit()
	session["uid"] = uid
	session["expires"] = datetime.now()
	return True

def authenticate(user):
	''' authenticates attempted login'''
	# checks if user exists in database
	c = get_db()#
	resultHash = c.cursor().execute(''' 
		Select hash, uid from Users  
		where email=?
	''',(user.email,)).fetchone()
	if resultHash is None:
		return redirect(url_for('login'))
	elif check_password(user.password, resultHash[0], pep):
		session["uid"] = resultHash[1]
		session["expires"] = datetime.now()

def logout_helper():
	session["uid"] = None

# ROUTES ----------------------------------------------------------------
def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		# check that session has a uid that is still good
		uid = session.get("uid")
		try:
			exp = session.get("expires")
		except ValueError:
			exp = None
		# if uid or exp is missing or exp has passed . . .
		if uid is None or exp is None or exp > (datetime.now() + timedelta(hours=1)):
			return redirect(url_for("login"))
		# only if the user is logged in should the route handler run
		return f(*args, **kwargs)
	return wrapper

@app.route('/')
def home():
	uid = session.get("uid")
	try:
		exp = session.get("expires")
	except:
		exp = None
	if uid is None or exp is None or exp > (datetime.now() + timedelta(hours=1)):
		return render_template("home.j2", user=None)
	else:
		db = get_db()
		usr = db.cursor().execute('''
		select fname, lname, email from users where uid=?
		''',(uid, )).fetchone()
		return render_template("home.j2", user=usr)

@app.route("/logout/")
def logout():
	logout_helper()
	return redirect(url_for("home"))

@app.route('/products/<int:productID>')
@login_required
def products(productID):
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
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User(form.email.data, form.password.data, form.fname.data, form.lname.data)
		if db_add(user):
			return redirect(url_for('home'))
		
	form = RegistrationForm()
	return render_template('register.j2', form=form) 

@app.route('/contact')
@login_required
def contact():
	return "this is the contact us page"

@app.route('/terms')
@login_required
def terms():
	return "this is the terms page"