from flask.ext.login import current_user
from werkzeug.exceptions import BadRequest

from auth import lm
from models import Annotation
from models import Document


def needs_login(**kwargs):
    if not current_user.is_authenticated():
        return lm.unauthorized()


def annotation_auth_delete(instance_id=None, **kwargs):
    ann = Annotation.query.get(instance_id)
    if not ann.editable_by(current_user):
        return lm.unauthorized()


def annotation_auth_create(data=None):
    docid = data['doc']
    if not current_user.can_annotate(docid):
        return lm.unauthorized()


def annotation_doc_exists(data=None):
    docid = data['doc']
    doc_obj = Document.query.get(docid)
    if doc_obj is None:
        raise BadRequest()


def annotation_decode_state(data=None):
    if 'state' not in data:
        data['state'] = 'open'
    data['state'] = Annotation.state_decode(data['state'])


def annotation_move_value_to_text(data=None):
    data['text'] = data['value']
    del data['value']


def annotation_check_type(data=None):
    keys = ['doc', 'page', 'posx', 'posy', 'width', 'height']
    for key in keys:
        if not isinstance(data[key], int):
            raise BadRequest()


def annotation_current_user(data=None):
    data['user'] = current_user.id


def make_api(manager):
    manager.create_api(Annotation,
                       methods=['DELETE', 'POST'],
                       preprocessors={
                           'DELETE': [annotation_auth_delete],
                           'POST': [needs_login,
                                    annotation_auth_create,
                                    annotation_doc_exists,
                                    annotation_check_type,
                                    annotation_decode_state,
                                    annotation_move_value_to_text,
                                    annotation_current_user,
                                    ],
                           },
                       )
