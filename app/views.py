import os.path

import koremutake
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for
from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import TextField

from .document import UploadForm
from .models import Annotation
from .models import Document
from .tools import kore_id

bp = Blueprint('bp', __name__)


@bp.route('/')
def home():
    """
    Home page.
    """
    kwargs = {'form': UploadForm()}
    if current_user.is_authenticated():
        documents = Document.mine()
        kwargs['documents'] = documents
        annotations = Annotation.mine()
        kwargs['annotations'] = annotations
    return render_template('home.html', **kwargs)


@bp.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


def page_not_found():
    return (render_template('404.html'), 404)


@bp.route('/502')
def internal_server_error():
    return (render_template('502.html'), 502)
