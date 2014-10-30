"""
SQLAlchemy models
"""
import random
from flask.ext.sqlalchemy import SQLAlchemy
import bcrypt
import string
import os.path
from flask import current_app

"""
The main DB object. It gets initialized in create_app.
"""
db = SQLAlchemy()


ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    """
    Application user. Someone that can log in.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_USER, nullable=False)

    def __init__(self, login, password, workfactor=12):
        self.name = login
        salt = bcrypt.gensalt(workfactor)
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt)

    def is_active(self):
        """
        Needed for flask-login.
        """
        return True

    def is_authenticated(self):
        """
        Needed for flask-login.
        """
        return True

    def get_id(self):
        """
        Needed for flask-login.
        """
        return unicode(self.id)

    def is_admin(self):
        """
        Has the user got administrative rights?
        This grants access to admin panel, so careful.
        """
        return (self.role == ROLE_ADMIN)

    @staticmethod
    def generate(fake):
        username = fake.user_name()
        password = fake.password()
        user = User(username, password, workfactor=4)
        return user


"""
A document. The actual file is stored in the application's instance path.
"""
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    filename = db.Column(db.String, nullable=False)

    def __init__(self, filename):
        self.id = random.randint(0, 0x7fffffff)
        self.filename = filename

    @staticmethod
    def generate(pdfdata):
        def fake_filename():
            letters = string.ascii_lowercase
            length = 8
            extension = '.pdf'
            base = ''.join(random.choice(letters) for _ in range(length))
            return base + extension

        filename = fake_filename()
        fullname = os.path.join(current_app.instance_path, 'uploads', filename)
        with open(fullname, 'w') as file:
            file.write(pdfdata)
        doc = Document(filename)
        return doc


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    doc_obj = db.relationship('Document', backref=db.backref('documents', lazy='dynamic'))

    def __init__(self, doc, text):
        self.doc = doc
        self.text = text

    @staticmethod
    def generate(fake, doc):
        text = fake.text()
        comm = Comment(doc, text)
        return comm


class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    page = db.Column(db.Integer, nullable=False)
    posx = db.Column(db.Integer, nullable=False)
    posy = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey(User.id))
    doc_obj = db.relationship('Document', backref=db.backref('document', lazy='dynamic'))
    user_obj = db.relationship('User', backref=db.backref('annotations', lazy='dynamic'))


    def __init__(self, doc, page, posx, posy, width, height, text, user):
        self.doc = doc
        self.page = page
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text
        self.user = user

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

    def editable_by(self, user):
        return user.is_authenticated() and user.id == self.user

    @staticmethod
    def generate(fake, doc, user):
        page = fake.random_int(1, 5)
        posx = fake.random_int(0, 300)
        posy = fake.random_int(0, 600)
        width = fake.random_int(50, 300)
        height = fake.random_int(50, 300)
        text = fake.text()
        ann = Annotation(doc, page, posx, posy, width, height, text, user)
        return ann


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
