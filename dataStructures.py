from wtforms import *

class RegistrationForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ]) 
    confirm = PasswordField('Confirm Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
    ]) 


class User:
    email = ""
    password = ""

    def __init__(self, email, password):
        self.email = email#
        self.password = password

class Product:
    pass