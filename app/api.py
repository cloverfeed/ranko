from flask.ext.login import current_user

from auth import lm
from models import Annotation


def annotation_check_auth(instance_id=None, **kwargs):
    ann = Annotation.query.get(instance_id)
    if not ann.editable_by(current_user):
        return lm.unauthorized()


def make_api(manager):
    manager.create_api(Annotation,
                       methods=['DELETE'],
                       preprocessors=dict(DELETE=[annotation_check_auth]),
                       )
