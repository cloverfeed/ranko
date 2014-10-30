from flask import flash, redirect, url_for, render_template, request
from flask import Blueprint
from flask import jsonify
from flask import send_from_directory
from flask import current_app
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import TextAreaField, HiddenField
from .models import db, Comment, Document, Annotation, Revision
import os.path
from .uploads import documents, documents_dir
import koremutake
from flask.ext.login import current_user, login_required
from .auth import lm


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
    return render_template('home.html', form=UploadForm())


class UploadForm(Form):
    file = FileField('The file to review')


@bp.route('/upload', methods=['POST'])
def upload():
    """
    Form to upload a document.

    :query revises: ID this doc is a new revision of.
    """
    form = UploadForm()
    if form.validate_on_submit():
        filename = documents.save(form.file.data)
        doc = Document(filename)
        db.session.add(doc)
        db.session.commit()
        revises = request.args.get('revises')
        if revises is not None:
            revises = kore_id(revises)
            (project, oldrev) = Revision.project_for(revises)
            revision = Revision(project, oldrev+1, doc.id)
            db.session.add(revision)
            db.session.commit()
        flash('Uploaded')
        return redirect(url_for('.view_doc', id=koremutake.encode(doc.id)))


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
    form_comm = CommentForm(docid=id)
    form_up = UploadForm()
    comments = Comment.query.filter_by(doc=id)
    annotations = Annotation.query.filter_by(doc=id)
    return render_template('view.html',
                           doc=doc,
                           form_comm=form_comm,
                           form_up=form_up,
                           comments=comments,
                           annotations=annotations,
                           )


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
    return send_from_directory(documents_dir(current_app), doc.filename)


@bp.route('/annotation/new', methods=['POST'])
@login_required
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
    user = current_user.id
    ann = Annotation(doc, page, posx, posy, width, height, text, user)
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
    """
    ann = Annotation.query.get(id)
    if not ann.editable_by(current_user):
        return lm.unauthorized()
    ann.load_json(request.form)
    db.session.commit()
    return jsonify(status='ok')


@bp.route('/view/<id>/revisions')
def view_revisions(id):
    """
    View all the Revisions associated to a document.
    """
    id = kore_id(id)
    history = Revision.history(id)
    revs = ((koremutake.encode(rev.doc), rev.version) for rev in history)
    return render_template('revisions.html', revs=revs)
