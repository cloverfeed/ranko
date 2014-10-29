"""
SQLAlchemy models
"""
import random
from flask.ext.sqlalchemy import SQLAlchemy

"""
The main DB object. It gets initialized in create_app.
"""
db = SQLAlchemy()

"""
A document. The actual file is stored in the application's instance path.
"""
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    filename = db.Column(db.String, nullable=False)

    def __init__(self, filename):
        self.id = random.randint(0, 0x7fffffff)
        self.filename = filename


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, doc, text):
        self.doc = doc
        self.text = text


class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    page = db.Column(db.Integer, nullable=False)
    posx = db.Column(db.Integer, nullable=False)
    posy = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, doc, page, posx, posy, width, height, text):
        self.doc = doc
        self.page = page
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text

    def to_json(self):
        return {'id': self.id,
                'posx': self.posx,
                'posy': self.posy,
                'width': self.width,
                'height': self.height,
                'text': self.text,
                }

    def load_json(self, data):
        self.posx = data['posx']
        self.posy = data['posy']
        self.width = data['width']
        self.height = data['height']
        self.text = data['value']


"""
History of a document.

A project is several docs, each of one has a version.
Version numbers are integers, and history is sequential.
"""
class Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    project = db.Column(db.Integer, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)

    def __init__(self, project, version, doc):
        self.project = project
        self.version = version
        self.doc = doc

    @staticmethod
    def project_for(doc):
        """
        Find the project associated to a given doc.
        Returns (project id, current version)
        Insert the initial revision if it does not exist.
        """
        rev = Revision.query.filter_by(doc=doc).first()
        if rev is not None:
            return (rev.project, rev.version)
        else:
            v1 = Revision(doc, 1, doc)
            db.session.add(v1)
            db.session.commit()
            return (doc, 1)

    @staticmethod
    def history(doc):
        (project, _) = Revision.project_for(doc)
        revs = Revision.query.filter_by(project=project)
        return revs
