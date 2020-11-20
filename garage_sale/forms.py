from wtforms import *


class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])
    submit = SubmitField('Submit')


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
