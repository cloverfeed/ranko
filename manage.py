"""
Flask-script stuff
"""
from flask.ext.migrate import MigrateCommand, stamp
from flask.ext.script import Manager
from app.factory import create_app
from app.models import db, User, ROLE_ADMIN
from mixer.backend.sqlalchemy import Mixer
from app.models import Document, Comment
import faker
import string
import random

class AppMixer(Mixer):
    def populate_target(self, values):
        import ipdb;ipdb.set_trace()
        target = self.__scheme(**values)
        return target

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
            doc = Document(filename)
            return doc

        def generate_comment(docs):
            doc = random_id(docs)
            assert doc is not None
            text = fake.text()
            comm = Comment(doc, text)
            return comm

        docs = [generate_document() for _ in range(0, 10)]
        comments = [generate_comment(docs) for _ in range(0, 20)]

        for obj in docs + comments:
            db.session.add(obj)
        db.session.commit()

    manager.run()

if __name__ == '__main__':
    main()
