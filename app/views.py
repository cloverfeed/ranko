import os.path

import koremutake
from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.wtf import Form
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Unauthorized
from wtforms import TextField

from .auth import lm
from .document import UploadForm
from .models import Annotation
from .models import db
from .models import Document
from .tools import kore_id
from .uploads import documents_dir

bp = Blueprint('bp', __name__)


def coerce_to(typ, val):
    """
    Raise a BadRequest (400) exception if the value cannot be converted to the
    given type.
    Return unconverted value
    """
    try:
        typ(val)
    except ValueError:
        raise BadRequest()
    return val


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
def view_favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@bp.route('/raw/<id>')
def rawdoc(id):
    """
    Get the file associated to a Document.

    :param id: A numeric (or koremutake) id.
    """
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    return send_from_directory(documents_dir(current_app), doc.filename)


@bp.route('/annotation/new', methods=['POST'])
@login_required
def annotation_new():
    """
    Create a new annotation.

    Note that the geometry depends on a particular scale,
    as they are in pixels.

    :<json int doc: Document ID.
    :<json int page: Page it's on.
    :<json int posx: X position on the page.
    :<json int posy: Y position on the page.
    :<json int width: Width of the annotation.
    :<json int height: Height of the annotation.
    :<json string value: The text content of the annotation.
    :<json string state: Optional state: "open" (default), "closed"

    :>json int id: The new ID.

    :status 400: Document ID does not exist.
    """
    doc = coerce_to(int, request.form['doc'])
    page = coerce_to(int, request.form['page'])
    posx = coerce_to(int, request.form['posx'])
    posy = coerce_to(int, request.form['posy'])
    width = coerce_to(int, request.form['width'])
    height = coerce_to(int, request.form['height'])
    text = request.form['value']
    state = Annotation.STATE_OPEN
    if 'state' in request.form:
        state = Annotation.state_decode(request.form['state'])
    doc_obj = Document.query.get(doc)
    if doc_obj is None:
        return BadRequest()
    if not current_user.can_annotate(doc):
        return Unauthorized()
    user = current_user.id
    ann = Annotation(doc, page, posx, posy, width, height, text, user,
                     state=state)
    db.session.add(ann)
    db.session.commit()
    return jsonify(id=ann.id)


@bp.route('/view/<id>/annotations')
def annotations_for_doc(id):
    """
    Get the annotations associated to a Document.

    :param id: Integer ID
    :>json array data: Results
    """
    data = {}
    for ann in Annotation.query.filter_by(doc=id):
        page = ann.page
        if page not in data:
            data[page] = []
        data[page].append(ann.to_json())
    return jsonify(data=data)


@bp.route('/annotation/<id>', methods=['DELETE'])
def annotation_delete(id):
    """
    Delete an annotation.

    :param id: Integer ID
    :>json string status: The string 'ok'
    """
    ann = Annotation.query.get(id)
    if not ann.editable_by(current_user):
        return lm.unauthorized()
    db.session.delete(ann)
    db.session.commit()
    return jsonify(status='ok')


@bp.route('/annotation/<id>', methods=['PUT'])
def annotation_edit(id):
    """
    Edit an Annotation.

    For JSON parameters, see :py:func:`annotation_new`.

    :>json string status: The string 'ok'
    """
    ann = Annotation.query.get(id)
    if not ann.editable_by(current_user):
        return lm.unauthorized()
    ann.load_json(request.form)
    db.session.commit()
    return jsonify(status='ok')
