from flask import Flask, render_template, flash, redirect, url_for
from flask.ext.wtf import Form
from flask_wtf.file import FileField
import os
from key import get_secret_key
from flask.ext.uploads import UploadSet
from flask.ext.uploads import configure_uploads
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('Review')

# CSRF & WTForms
key_file = os.path.join(app.instance_path, 'secret.key')
app.config['SECRET_KEY'] = get_secret_key(key_file)

# flask-uploads
documents = UploadSet('documents', extensions=['pdf'],
        default_dest=lambda app: os.path.join(app.instance_path, 'uploads'))
configure_uploads(app, [documents])

# flask-sqlalchemy
uri = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    filename = db.Column(db.String, nullable=False)

    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def get_by_id(id):
        return db.session.query(Document).get(id)


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

@app.route('/view/<id>')
def view_doc(id):
    doc = Document.get_by_id(id)
    return render_template('view.html', doc=doc)

def main():
    pass
    app.run(debug=True)

if __name__ == '__main__':
    main()
