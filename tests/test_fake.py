import faker

from app.models import Annotation
from app.models import Comment
from app.models import Document
from app.models import User
from common import RankoTestCase


class FakeTestCase(RankoTestCase):
    def test_generate_models(self):
        fake = faker.Faker()
        user = User.generate(fake)
        doc = Document.generate('pdfdata')
        comm = Comment.generate(fake, doc)
        ann = Annotation.generate(fake, doc, user)
