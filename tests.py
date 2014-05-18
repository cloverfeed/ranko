from app import app, db
from key import get_secret_key
import unittest
import os
from flask.ext.uploads import TestingFileStorage


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['WTF_CSRF_ENABLED'] = False

        uri = 'sqlite:///' + os.path.join(app.instance_path, 'test.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = uri

        self.key_file = os.path.join(app.instance_path, 'secret-test.key')
        app.config['SECRET_KEY'] = get_secret_key(self.key_file)

        self.app = app.test_client()
        db.create_all()

    def test_home(self):
        r = self.app.get('/')
        self.assertIn('Upload and review', r.data)

    def test_upload(self):
        storage = TestingFileStorage(filename='toto.pdf')
        r = self.app.post('/upload', data={
                'file': storage
            })
        self.assertEqual(r.status_code, 302)
        self.assertIn('/view/', r.location)
