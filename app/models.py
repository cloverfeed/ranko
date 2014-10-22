"""
SQLAlchemy models
"""
from app import db
import random

"""
A document. The actual file is stored in the application's instance path.
"""
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    filename = db.Column(db.String, nullable=False)

    def __init__(self, filename):
        self.id = random.randint(0, 0xffffffff)
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
