from wtforms import *


class RegistrationForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    fname = StringField('fname', [validators.required()])
    lname = StringField('lname', [validators.required()])
    submit = SubmitField('Submit')


class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])
    submit = SubmitField('Submit')


class User:
    email = ""
    password = ""
    fname = ""
    lname = ""

    def __init__(self, email, password, fname="", lname=""):
        self.email = email  #
        self.password = password
        self.fname = fname
        self.lname = lname


class Product:
    pass
