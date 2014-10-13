from flask import Flask
import os
from .key import get_secret_key
from flask.ext.uploads import UploadSet
from flask.ext.uploads import configure_uploads
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('Review')

app.config['pdfjs_version'] = '1.0.473'

# CSRF & WTForms
key_file = os.path.join(app.instance_path, 'secret.key')
app.config['SECRET_KEY'] = get_secret_key(key_file)


# flask-uploads
def doc_dest(app):
    return os.path.join(app.instance_path, 'uploads')
documents = UploadSet('documents', extensions=['pdf'], default_dest=doc_dest)
configure_uploads(app, [documents])

# flask-sqlalchemy
uri = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

import views
