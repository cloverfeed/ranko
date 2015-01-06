from flask import Blueprint
from flask import flash
from flask import redirect
from flask import url_for
from flask.ext.login import current_user
from flask.ext.wtf import Form
from werkzeug.exceptions import Unauthorized
from wtforms import HiddenField
from wtforms import TextAreaField

from .models import Comment
from .models import db
from .tools import kore_id

comment = Blueprint('comment', __name__)


class CommentForm(Form):
    docid = HiddenField('Document ID')
    comment = TextAreaField('Comment')


@comment.route('/comment/new', methods=['POST'])
def new():
    """
    Create a new comment.

    :status 302: Redirects to the "view document" page.
    :status 401: Not allowed to comment.
    """
    form = CommentForm()
    assert(form.validate_on_submit())
    docid = kore_id(form.docid.data)
    if not current_user.is_authenticated():
        return Unauthorized()
    if not current_user.can_comment_on(docid):
        return Unauthorized()
    comm = Comment(docid, form.comment.data)
    db.session.add(comm)
    db.session.commit()
    flash("Comment saved")
    return redirect(url_for('document.view_doc', id=form.docid.data))
