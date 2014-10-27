from app import app, db, documents
from flask import flash, redirect, url_for, render_template, request
from flask import send_from_directory, jsonify
from flask import Blueprint
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import TextAreaField, HiddenField
from .models import Comment, Document, Annotation
import os.path
import koremutake


bp = Blueprint('bp', __name__)


def kore_id(s):
    """
    Decode the string into an integer.
    It can be a koremutake or a decimal number.
    """
    try:
        r = koremutake.decode(s)
    except ValueError:
        r = int(s)
    return r


@bp.route('/')
def home():
    """
    Home page.
    """
    return render_template('home.html')


class UploadForm(Form):
    file = FileField('The file to review')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Form to upload a document.
    """
    form = UploadForm()
    if form.validate_on_submit():
        filename = documents.save(form.file.data)
        doc = Document(filename)
        db.session.add(doc)
        db.session.commit()
        flash('Uploaded')
        return redirect(url_for('.view_doc', id=koremutake.encode(doc.id)))
    return render_template('upload.html', form=form)


class CommentForm(Form):
    docid = HiddenField('Document ID')
    comment = TextAreaField('Comment')


@bp.route('/view/<id>')
def view_doc(id):
    """
    View a Document.

    :param id: A numeric (or koremutake) id.
    """
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    form = CommentForm(docid=id)
    comments = Comment.query.filter_by(doc=id)
    annotations = Annotation.query.filter_by(doc=id)
    return render_template('view.html', doc=doc, form=form,
                           comments=comments, annotations=annotations)


@bp.route('/comment/new', methods=['POST'])
def post_comment():
    """
    Create a new comment.

    :status 302: Redirects to the "view document" page.
    """
    form = CommentForm()
    assert(form.validate_on_submit())
    docid = kore_id(form.docid.data)
    comm = Comment(docid, form.comment.data)
    db.session.add(comm)
    db.session.commit()
    flash("Comment saved")
    return redirect(url_for('.view_doc', id=form.docid.data))


@bp.route('/raw/<id>')
def rawdoc(id):
    """
    Get the file associated to a Document.

    :param id: A numeric (or koremutake) id.
    """
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    docdir = os.path.join(app.instance_path, 'uploads')
    return send_from_directory(docdir, doc.filename)


@bp.route('/annotation/new', methods=['POST'])
def annotation_new():
    """
    Create a new annotation.

    :>json int id: The new ID.
    """
    doc = request.form['doc']
    page = request.form['page']
    posx = request.form['posx']
    posy = request.form['posy']
    width = request.form['width']
    height = request.form['height']
    text = request.form['value']
    ann = Annotation(doc, page, posx, posy, width, height, text)
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
    db.session.delete(ann)
    db.session.commit()
    return jsonify(status='ok')


@bp.route('/annotation/<id>', methods=['PUT'])
def annotation_edit(id):
    """
    Edit an Annotation.
    """
    ann = Annotation.query.get(id)
    ann.load_json(request.form)
    db.session.commit()
    return jsonify(status='ok')
