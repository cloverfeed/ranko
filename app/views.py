import os.path

import koremutake
from flask import Blueprint
from flask import current_app
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.uploads import UploadNotAllowed
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from werkzeug.exceptions import BadRequest
from wtforms import HiddenField
from wtforms import TextAreaField
from wtforms import TextField

from .auth import lm
from .models import Annotation
from .models import AudioAnnotation
from .models import Comment
from .models import db
from .models import Document
from .models import Revision
from .uploads import documents
from .uploads import documents_dir

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


class UploadForm(Form):
    file = FileField('The file to review')
    title = TextField('Title', description='The title of your document (may be blank)')


@bp.route('/upload', methods=['POST'])
def upload():
    """
    Form to upload a document.

    :query revises: ID this doc is a new revision of.
    """
    form = UploadForm()
    if form.validate_on_submit():
        try:
            filename = documents.save(form.file.data)
        except UploadNotAllowed:
            flash('Unsupported file type')
            return redirect(url_for('.home'))
        doc = Document(filename, title=form.title.data)
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
    readOnly = not current_user.is_authenticated()
    return render_template('view.html',
                           doc=doc,
                           form_comm=form_comm,
                           form_up=form_up,
                           comments=comments,
                           annotations=annotations,
                           readOnly=readOnly,
                           )


@bp.route('/view/<id>/list')
def view_list(id):
    """
    View the set of annotations on a document.
    """
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    if doc.filetype == 'pdf' or doc.filetype == 'image':
        annotations = Annotation.query.filter_by(doc=id)
        template = 'list.html'
    elif doc.filetype == 'audio':
        annotations = AudioAnnotation.query.filter_by(doc_id=id)
        template = 'list_audio.html'
    else:
        assert False, 'Unknown filetype: {}'.format(doc.filetype)
    return render_template(template,
                           doc=doc,
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


@bp.route('/view/<id>/revisions')
def view_revisions(id):
    """
    View all the Revisions associated to a document.
    """
    id = kore_id(id)
    history = Revision.history(id)
    revs = ((koremutake.encode(rev.doc), rev.version) for rev in history)
    return render_template('revisions.html', revs=revs)


class EditForm(Form):
    title = TextField('Title', description='The title of your document')


@bp.route('/view/<id>/edit', methods=['GET', 'POST'])
def edit_doc(id):
    """
    Edit the document's metadata.
    """
    id = kore_id(id)
    form = EditForm()
    delete_form = DeleteForm()
    if form.validate_on_submit():
        doc = Document.query.get(id)
        doc.title = form.title.data
        db.session.commit()
        return redirect(url_for('.view_doc', id=id))
    delete_action = url_for('.delete_doc', id=id)
    return render_template('edit.html',
                           form=form,
                           delete_form=delete_form,
                           delete_action=delete_action)


class DeleteForm(Form):
    pass


@bp.route('/view/<id>/delete', methods=['POST'])
def delete_doc(id):
    """
    Delete the document.
    """
    id = kore_id(id)
    form = DeleteForm()
    if form.validate_on_submit():
        doc = Document.query.get(id)
        doc.delete()
        return redirect(url_for('.home'))
    return redirect(url_for('.view_doc', id=id))
