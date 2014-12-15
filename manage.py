"""
Flask-script stuff
"""
import base64
import os
import os.path
import random
import string
import sys
from random import choice

import faker
from flask.ext.migrate import MigrateCommand
from flask.ext.migrate import stamp
from flask.ext.script import Manager

from app.factory import create_app
from app.models import Annotation
from app.models import Comment
from app.models import db
from app.models import Document
from app.models import ROLE_ADMIN
from app.models import User


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


def generate_password():
    letters = string.ascii_letters + string.digits
    length = 20
    password = ''.join(random.choice(letters) for _ in range(length))
    return password


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
        password = generate_password()
        user = User('admin', password)
        user.role = ROLE_ADMIN
        db.session.add(user)
        db.session.commit()
        print password

    @manager.command
    def fake():
        "Populate tables using fake data"
        fake = faker.Faker()

        upload_dir = os.path.join(manager.app.instance_path, 'uploads')
        if not os.path.isdir(upload_dir):
            os.mkdir(upload_dir)

        users = [User.generate(fake) for _ in range(0, 10)]
        user = users[0]

        for obj in users:
            db.session.add(obj)
        db.session.commit()

        pdfdata = base64.decodestring(EMPTY_PDF.strip())
        docs = [Document.generate(pdfdata) for _ in range(0, 10)]

        for doc in docs:
            comments = [Comment.generate(fake, doc.id) for _ in range(0, 4)]
            annotations = [Annotation.generate(fake, doc.id, user.id)
                           for _ in range(0, 2)]

        for obj in docs + comments + annotations:
            db.session.add(obj)
        db.session.commit()

    @manager.command
    def resetpassword(username):
        "Reset password for a user"
        user = User.query.filter_by(name=username).first()
        if user is None:
            print "No such user."
            sys.exit(1)
        password = generate_password()
        user.set_password(password)
        db.session.commit()
        print password

    manager.run()

if __name__ == '__main__':
    main()
