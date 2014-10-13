from app import app, db, documents
from flask import flash, redirect, url_for, render_template
from flask import send_from_directory
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import TextAreaField, HiddenField
from .models import Comment, Document
import os.path


@app.route('/')
def home():
    return render_template('home.html')


class UploadForm(Form):
    file = FileField('The file to review')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        filename = documents.save(form.file.data)
        doc = Document(filename)
        db.session.add(doc)
        db.session.commit()
        flash('Uploaded')
        return redirect(url_for('view_doc', id=doc.id))
    return render_template('upload.html', form=form)


class CommentForm(Form):
    docid = HiddenField('Document ID')
    comment = TextAreaField('Comment')


@app.route('/view/<id>')
def view_doc(id):
    doc = Document.get_by_id(id)
    form = CommentForm(docid=id)
    comments = Comment.all_for_doc(id)
    return render_template('view.html', doc=doc, form=form, comments=comments)


@app.route('/comment/new', methods=['POST'])
def post_comment():
    form = CommentForm()
    assert(form.validate_on_submit())
    docid = form.docid.data
    comm = Comment(docid, form.comment.data)
    db.session.add(comm)
    db.session.commit()
    flash("Comment saved")
    return redirect(url_for('view_doc', id=form.docid.data))


@app.route('/raw/<id>')
def rawdoc(id):
    doc = Document.get_by_id(id)
    docdir = os.path.join(app.instance_path, 'uploads')
    return send_from_directory(docdir, doc.filename)
