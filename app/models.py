"""
SQLAlchemy models
"""
import os
import os.path
import random
import string

import bcrypt
import koremutake
from flask import current_app
from flask.ext.login import current_user
from flask.ext.sqlalchemy import SQLAlchemy

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
        self.set_password(password, workfactor=workfactor)

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

    def set_password(self, clear, workfactor=12):
        salt = bcrypt.gensalt(workfactor)
        self.password = bcrypt.hashpw(clear.encode('utf-8'), salt)


class Document(db.Model):
    """
    A document. The actual file is stored in the application's instance path.
    """
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    filename = db.Column(db.String, nullable=False)
    filetype = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    title = db.Column(db.String, nullable=True)

    def __init__(self, filename, title=None):
        self.id = random.randint(0, 0x7fffffff)
        self.filename = filename
        self.filetype = Document.detect_filetype(filename)
        user_id = None
        if current_user.is_authenticated():
            user_id = current_user.id
        self.user_id = user_id
        self.title = title

    def delete(self):
        """
        Remove this document from the DB and filesystem.
        """
        db.session.delete(self)
        db.session.commit()
        os.unlink(self.full_path())

    def full_path(self):
        return Document.full_path_to(self.filename)

    @staticmethod
    def full_path_to(filename):
        return os.path.join(current_app.instance_path, 'uploads', filename)

    @staticmethod
    def detect_filetype(filename):
        if filename.endswith('.pdf'):
            return 'pdf'
        elif filename.endswith('.png'):
            return 'image'
        elif filename.endswith('.mp3'):
            return 'audio'
        else:
            assert False, "Unknown file extension in file {}".format(filename)

    @staticmethod
    def generate(pdfdata):
        def fake_filename():
            letters = string.ascii_lowercase
            length = 8
            extension = '.pdf'
            base = ''.join(random.choice(letters) for _ in range(length))
            return base + extension

        filename = fake_filename()
        fullname = Document.full_path_to(filename)
        with open(fullname, 'w') as file:
            file.write(pdfdata)
        doc = Document(filename)
        return doc

    @staticmethod
    def mine():
        assert(current_user.is_authenticated())
        uid = current_user.id
        return Document.query.filter_by(user_id=uid)

    def title_or_id(self):
        if self.title is None:
            return koremutake.encode(self.id)
        return self.title

    def icon_class_filetype(self):
        if self.filetype == 'pdf':
            return 'glyphicon glyphicon-file'
        if self.filetype == 'image':
            return 'glyphicon glyphicon-picture'
        if self.filetype == 'audio':
            return 'glyphicon glyphicon-music'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    doc_obj = db.relationship('Document', backref=db.backref('documents',
                                                             lazy='dynamic'))

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
    state = db.Column(db.SmallInteger, nullable=False, default=0)
    doc_obj = db.relationship('Document', backref=db.backref('document',
                                                             lazy='dynamic'))
    user_obj = db.relationship('User', backref=db.backref('annotations',
                                                          lazy='dynamic'))

    STATE_OPEN = 0
    STATE_CLOSED = 1

    @staticmethod
    def state_encode(state):
        d = {Annotation.STATE_OPEN: 'open',
             Annotation.STATE_CLOSED: 'closed',
             }
        return d[state]

    @staticmethod
    def state_decode(string):
        d = {'open': Annotation.STATE_OPEN,
             'closed': Annotation.STATE_CLOSED,
             }
        return d[string]

    def __init__(self, doc, page, posx, posy,
                 width, height, text, user, state):
        self.doc = doc
        self.page = page
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text
        self.user = user
        self.state = state

    def to_json(self):
        return {'id': self.id,
                'posx': self.posx,
                'posy': self.posy,
                'width': self.width,
                'height': self.height,
                'text': self.text,
                'state': Annotation.state_encode(self.state)
                }

    def load_json(self, data):
        if 'posx' in data:
            self.posx = data['posx']
        if 'posy' in data:
            self.posy = data['posy']
        if 'width' in data:
            self.width = data['width']
        if 'height' in data:
            self.height = data['height']
        if 'value' in data:
            self.text = data['value']
        if 'state' in data:
            self.state = Annotation.state_decode(data['state'])

    def editable_by(self, user):
        return user.is_authenticated() and user.id == self.user

    @staticmethod
    def generate(fake, doc, user):
        page = fake.random_int(1, 5)
        posx = fake.random_int(0, 300)
        posy = fake.random_int(0, 600)
        width = fake.random_int(50, 300)
        height = fake.random_int(50, 300)
        if fake.boolean():
            state = Annotation.STATE_OPEN
        else:
            state = Annotation.STATE_CLOSED
        text = fake.text()
        ann = Annotation(doc, page, posx, posy, width, height, text, user, state)
        return ann

    def is_closed(self):
        return self.state == Annotation.STATE_CLOSED

    @staticmethod
    def mine():
        assert(current_user.is_authenticated())
        return Annotation.query.filter_by(user=current_user.id)


class Revision(db.Model):
    """
    History of a document.

    A project is several docs, each of one has a version.
    Version numbers are integers, and history is sequential.
    """
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


class AudioAnnotation(db.Model):
    """
    Annotation for an audio document.

    This is somehow simpler than for pdf documents since they are 1D only.

    start and length are in seconds.
    """
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    start = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=False)
    state = db.Column(db.SmallInteger, nullable=False, default=0)

    def __init__(self, user_id, doc_id, start, length, text):
        self.user_id = user_id
        self.doc_id = doc_id
        self.start = start
        self.length = length
        self.text = text
        self.state = Annotation.STATE_OPEN

    def to_json(self):
        return {'id': self.id,
                'user': self.user_id,
                'doc': self.doc_id,
                'start': self.start,
                'length': self.length,
                'text': self.text,
                'state': Annotation.state_encode(self.state)
                }

    def load_json(self, data):
        if 'start' in data:
            self.start = data['start']
        if 'length' in data:
            self.length = data['length']
        if 'text' in data:
            self.text = data['text']
        if 'state' in data:
            self.state = Annotation.state_decode(data['state'])

    def editable_by(self, user):
        return user.is_authenticated() and user.id == self.user_id

    def is_closed(self):
        return self.state == Annotation.STATE_CLOSED
