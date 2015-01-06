from flask import Blueprint
from flask import jsonify
from flask import request
from flask.ext.login import current_user
from flask.ext.login import login_required
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Unauthorized

from .auth import lm
from .models import Annotation
from .models import db
from .models import Document
from .tools import coerce_to

annotation = Blueprint('annotation', __name__)


@annotation.route('/annotation/new', methods=['POST'])
@login_required
def new():
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


@annotation.route('/view/<id>/annotations')
def for_doc(id):
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


@annotation.route('/annotation/<id>', methods=['DELETE'])
def delete(id):
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


@annotation.route('/annotation/<id>', methods=['PUT'])
def edit(id):
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
