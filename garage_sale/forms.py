from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import validators, StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField

from garage_sale.data_structures import User, Product


class LoginForm(FlaskForm):
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])
    submit = SubmitField('Submit')

    def to_user(self):
        return User(
            self.email.data,
            self.password.data
        )


class RecoverPasswordForm(FlaskForm):
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    fname = StringField('First Name', [validators.required()])
    lname = StringField('Last Name', [validators.required()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
    profile_image = FileField("Profile Image", [FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit = SubmitField('Submit')

    def to_user(self):
        return User(
            self.email.data,
            self.password.data,
            self.fname.data,
            self.lname.data
        )


class SettingsForm(FlaskForm):
    email = StringField('Email', [validators.Email()])
    fname = StringField('First Name')
    lname = StringField('Last Name')
    password = PasswordField('New Password', [
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    profile_image = FileField("Profile Image", [FileAllowed(['jpg', 'png'], 'Images only!')])
    accept_changes = BooleanField('I accept these changes', [validators.DataRequired()])
    submit = SubmitField('Confirm Changes')

    def to_user(self):
        return User(
            self.email.data,
            self.password.data,
            self.fname.data,
            self.lname.data
        )


class CreateProductForm(FlaskForm):
    posting_title = StringField("Posting Title", [validators.Length(max=120), validators.DataRequired()])
    price = StringField("Price", [validators.regexp(r'^\$?([\d,]+(\.\d\d?)?)$'), validators.DataRequired()])
    description = TextAreaField("Description", [validators.Length(max=1000)])
    tags = TextAreaField("Tags (comma separated)")
    image_file = FileField("Image")
    condition = SelectField("Condition", choices=[("new", "New"), ("used", "Used")])
    create_posting = SubmitField("Create Posting")

    def to_product(self, user):
        return Product(
            self.posting_title.data,
            self.price.data,
            user,
            self.description.data,
            self.tags.data,
            self.image_file.data,
            self.condition.data
        )

    def from_product(self, product):
        self.posting_title.data = product.name
        self.price.data = product.price
        self.description.data = product.description
        self.tags.data = product.tags
        self.condition.data = product.condition
