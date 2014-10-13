from app import db


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    filename = db.Column(db.String, nullable=False)

    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def get_by_id(id):
        return Document.query.get_or_404(id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doc = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, doc, text):
        self.doc = doc
        self.text = text

    @staticmethod
    def all_for_doc(doc):
        return db.session.query(Comment).filter_by(doc=doc)
