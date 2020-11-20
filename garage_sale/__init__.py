import os
from functools import wraps

from flask import Flask, g
from flask_uploads import UploadSet, configure_uploads, IMAGES


def make_g(function):
    """Turns the result of the given function into a variable
    that is stored in the flask g object. The name in g will
    be the same as the function name"""

    @wraps(function)
    def wrapper():
        value = getattr(g, function.__name__, None)

        if value is None:
            value = function()
            setattr(g, function.__name__, value)

        return value

    return wrapper


server_dir = os.path.dirname(__file__)
image_dir = os.path.join(server_dir, 'images/users')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SECRET_KEY"] = "correcthorsebatterystaple"
app.config["UPLOADED_IMAGES_DEST"] = os.path.join(server_dir, "images/users")

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

import garage_sale.routes
