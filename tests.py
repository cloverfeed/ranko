from app import app, db
from key import get_secret_key
import unittest
import os


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
