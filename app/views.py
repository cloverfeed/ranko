from app import app, db, documents
from flask import flash, redirect, url_for, render_template, request
from flask import send_from_directory, jsonify
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import TextAreaField, HiddenField
from .models import Comment, Document, Annotation
import os.path
import koremutake


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
        return redirect(url_for('view_doc', id=koremutake.encode(doc.id)))
    return render_template('upload.html', form=form)


class CommentForm(Form):
    docid = HiddenField('Document ID')
    comment = TextAreaField('Comment')


@app.route('/view/<id>')
def view_doc(id):
    id = kore_id(id)
    doc = Document.query.get_or_404(id)
    form = CommentForm(docid=id)
    comments = Comment.query.filter_by(doc=id)
    annotations = Annotation.query.filter_by(doc=id)
    return render_template('view.html', doc=doc, form=form,
                           comments=comments, annotations=annotations)


@app.route('/comment/new', methods=['POST'])
def post_comment():
    form = CommentForm()
    assert(form.validate_on_submit())
    docid = kore_id(form.docid.data)
    comm = Comment(docid, form.comment.data)
    db.session.add(comm)
    db.session.commit()
    flash("Comment saved")
    return redirect(url_for('view_doc', id=form.docid.data))


@app.route('/raw/<id>')
def rawdoc(id):
    doc = Document.query.get_or_404(id)
    docdir = os.path.join(app.instance_path, 'uploads')
    return send_from_directory(docdir, doc.filename)


@app.route('/annotation/new', methods=['POST'])
def annotation_new():
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
    return text


@app.route('/view/<id>/annotations')
def annotations_for_doc(id):
    data = {}
    for ann in Annotation.query.filter_by(doc=id):
        page = ann.page
        if page not in data:
            data[page] = []
        data[page].append(ann.to_json())
    return jsonify(data=data)


@app.route('/annotation/<id>', methods=['DELETE'])
def annotation_delete(id):
    ann = Annotation.query.get(id)
    db.session.delete(ann)
    db.session.commit()
    return jsonify(status='ok')
