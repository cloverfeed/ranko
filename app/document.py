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
from flask.ext.login import login_user
from flask.ext.uploads import UploadNotAllowed
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from itsdangerous import BadSignature
from wtforms import TextField

from .auth import lm
from .auth import pseudo_user
from .auth import shared_link_serializer
from .comment import CommentForm
from .models import Annotation
from .models import AudioAnnotation
from .models import Comment
from .models import db
from .models import Document
from .models import Revision
from .tools import kore_id
from .uploads import documents
from .uploads import documents_dir

document = Blueprint('document', __name__)


class UploadForm(Form):
    file = FileField('The file to review')
    title = TextField('Title',
                      description='The title of your document (may be blank)')


@document.route('/upload', methods=['POST'])
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
            return redirect(url_for('bp.home'))
        title = form.title.data
        doc = Document(filename, title=title)
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
        return redirect(url_for('.view', id=koremutake.encode(doc.id)))


@document.route('/view/<id>')
def view(id):
    """
    View a Document.

    :param id: A numeric (or koremutake) id.
    """
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    form_comm = CommentForm(docid=id)
    form_up = UploadForm()
    form_share = ShareForm()
    comments = Comment.query.filter_by(doc=id)
    readOnly = not current_user.is_authenticated()
    can_edit = doc.editable_by(current_user)
    return render_template('view.html',
                           doc=doc,
                           form_comm=form_comm,
                           form_up=form_up,
                           form_share=form_share,
                           comments=comments,
                           readOnly=readOnly,
                           can_edit=can_edit,
                           )


@document.route('/raw/<id>')
def raw(id):
    """
    Get the file associated to a Document.

    :param id: A numeric (or koremutake) id.
    """
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    return send_from_directory(documents_dir(current_app), doc.filename)


@document.route('/view/<id>/revisions')
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


@document.route('/view/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    """
    Edit the document's metadata.
    """
    id = kore_id(id)
    form = EditForm()
    delete_form = DeleteForm()
    if form.validate_on_submit():
        doc = Document.query.get(id)
        if not doc.editable_by(current_user):
            return lm.unauthorized()
        doc.title = form.title.data
        db.session.commit()
        return redirect(url_for('.view', id=id))
    delete_action = url_for('.delete', id=id)
    return render_template('edit.html',
                           form=form,
                           delete_form=delete_form,
                           delete_action=delete_action)


class DeleteForm(Form):
    pass


@document.route('/view/<id>/delete', methods=['POST'])
def delete(id):
    """
    Delete the document.
    """
    id = kore_id(id)
    form = DeleteForm()
    if form.validate_on_submit():
        doc = Document.query.get(id)
        if not doc.editable_by(current_user):
            return lm.unauthorized()
        doc.delete()
        return redirect(url_for('bp.home'))


class ShareForm(Form):
    name = TextField('Name',
                     description='The person you are giving this link to')


@document.route('/view/<id>/share', methods=['POST'])
def share(id):
    form = ShareForm()
    if form.validate_on_submit():
        doc = Document.query.get(id)
        if not doc.shareable_by(current_user):
            return lm.unauthorized()
        data = {'doc': id,
                'name': form.name.data,
                }
        h = shared_link_serializer().dumps(data)
        return jsonify(data=h)


@document.route('/view/shared/<key>')
def view_shared(key):
    try:
        data = shared_link_serializer().loads(key)
    except BadSignature:
        flash('This link is invalid.')
        return redirect(url_for('bp.home'))
    docid = kore_id(data['doc'])
    doc = Document.query.get(docid)
    name = data['name']
    user = pseudo_user(name, docid)
    login_user(user)
    flash(u"Hello, {}!".format(name, 'utf-8'))
    return redirect(url_for('.view', id=doc.id))
