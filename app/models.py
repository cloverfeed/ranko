from app import db
import random


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
