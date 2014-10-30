"""
Flask-script stuff
"""
from flask.ext.migrate import MigrateCommand, stamp
from flask.ext.script import Manager
from app.factory import create_app
from app.models import db, User, ROLE_ADMIN
from mixer.backend.sqlalchemy import Mixer
from app.models import Document, Comment, Annotation
import faker
import string
import random
import os.path
import base64

class AppMixer(Mixer):
    def populate_target(self, values):
        import ipdb;ipdb.set_trace()
        target = self.__scheme(**values)
        return target

EMPTY_PDF = """
JVBERi0xLjIKJcfsj6IKNSAwIG9iago8PC9MZW5ndGggNiAwIFIvRmlsdGVyIC9GbGF0ZURlY29k
ZT4+CnN0cmVhbQp4nCtUMNAzVDAAQSidnMsVyAUANUkEZWVuZHN0cmVhbQplbmRvYmoKNiAwIG9i
agoyMwplbmRvYmoKNCAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCA1OTUuMjggODQx
Ljg5XQovUGFyZW50IDMgMCBSCi9SZXNvdXJjZXM8PC9Qcm9jU2V0Wy9QREZdCj4+Ci9Db250ZW50
cyA1IDAgUgo+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWwo0IDAgUgpd
IC9Db3VudCAxCj4+CmVuZG9iagoxIDAgb2JqCjw8L1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDMgMCBS
Cj4+CmVuZG9iagoyIDAgb2JqCjw8L1Byb2R1Y2VyKEdQTCBHaG9zdHNjcmlwdCA5LjA2KQovQ3Jl
YXRpb25EYXRlKEQ6MjAxNDEwMzAxMDM0MDgrMDEnMDAnKQovTW9kRGF0ZShEOjIwMTQxMDMwMTAz
NDA4KzAxJzAwJyk+PmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAz
MDUgMDAwMDAgbiAKMDAwMDAwMDM1MyAwMDAwMCBuIAowMDAwMDAwMjQ2IDAwMDAwIG4gCjAwMDAw
MDAxMjYgMDAwMDAgbiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMTA4IDAwMDAwIG4gCnRy
YWlsZXIKPDwgL1NpemUgNyAvUm9vdCAxIDAgUiAvSW5mbyAyIDAgUgovSUQgWzxCRDRERjFGODJB
QTQzMTY1Q0Y1QzkzNzY4QUU5MzQ5MD48QkQ0REYxRjgyQUE0MzE2NUNGNUM5Mzc2OEFFOTM0OTA+
XQo+PgpzdGFydHhyZWYKNDc2CiUlRU9GCg==
"""

def main():
    manager = Manager(create_app)
    manager.add_command('db', MigrateCommand)
    manager.add_option('-c', '--config', dest='config_file', required=False)

    @manager.command
    def create():
        "Creates database tables from sqlalchemy models"
        db.create_all()
        stamp()

    @manager.command
    def makeadmin():
        "Create an admin user with a random password"
        letters = string.ascii_letters + string.digits
        length = 20
        password = ''.join(random.choice(letters) for _ in range(length))
        user = User('admin', password)
        user.role = ROLE_ADMIN
        db.session.add(user)
        db.session.commit()
        print password

    @manager.command
    def fake():
        "Populate tables using fake data"
        fake = faker.Faker()

        def fake_filename():
            letters = string.ascii_lowercase
            length = 8
            extension = '.pdf'
            base = ''.join(random.choice(letters) for _ in range(length))
            return base + extension

        def random_id(objs):
            obj = random.choice(objs)
            return obj.id

        def generate_document():
            filename = fake_filename()
            fullname = os.path.join(manager.app.instance_path, 'uploads', filename)
            with open(fullname, 'w') as file:
                pdfdata = base64.decodestring(EMPTY_PDF.strip())
                file.write(pdfdata)
            doc = Document(filename)
            return doc

        def generate_comment(docs):
            doc = random_id(docs)
            assert doc is not None
            text = fake.text()
            comm = Comment(doc, text)
            return comm

        def generate_annotation(docs):
            doc = random_id(docs)
            page = fake.random_int(1, 5)
            posx = fake.random_int(0, 300)
            posy = fake.random_int(0, 600)
            width = fake.random_int(50, 300)
            height = fake.random_int(50, 300)
            text = fake.text()
            ann = Annotation(doc, page, posx, posy, width, height, text)
            return ann

        docs = [generate_document() for _ in range(0, 10)]
        comments = [generate_comment(docs) for _ in range(0, 20)]
        annotations = [generate_annotation(docs) for _ in range(0, 50)]

        for obj in docs + comments + annotations:
            db.session.add(obj)
        db.session.commit()

    manager.run()

if __name__ == '__main__':
    main()
