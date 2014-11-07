from flask import Blueprint
from flask import jsonify
from flask import request
from flask.ext.login import current_user

from models import AudioAnnotation
from models import db

audioann = Blueprint('audioann', __name__)

@audioann.route('/audioannotation/new', methods=['POST'])
def audioann_new():
    """
    Create a new audio annotation.

    :<json int doc: Document ID.
    :<json start: Start of annotation, in seconds
    :<json length: Length of annotation, in seconds
    :<json string text: The text content of the annotation.

    :>json int id: The new ID.
    """
    user = current_user.id
    doc = request.form['doc']
    start = request.form['start']
    length = request.form['length']
    text = request.form['text']
    aa = AudioAnnotation(user, doc, start, length, text)
    db.session.add(aa)
    db.session.commit()
    return jsonify(id=aa.id)


@audioann.route('/view/<id>/audioannotations')
def audio_annotations_for_doc(id):
    """
    Get the audio annotations associated to a Document.

    :param id: Integer ID
    :>json array data: Results
    """
    data = []
    for ann in AudioAnnotation.query.filter_by(doc_id=id):
        data.append(ann.to_json())
    return jsonify(data=data)
