from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask.ext.login import current_user
from flask.ext.login import login_required
from werkzeug.exceptions import Unauthorized

from .auth import lm
from .models import Annotation
from .models import db
from .models import Document

annotation = Blueprint('annotation', __name__)


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
