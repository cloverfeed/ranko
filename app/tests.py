from app import app, db
from .key import get_secret_key
import unittest
import os
from flask.ext.uploads import TestingFileStorage
import re


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

    # FIXME If called > 1, it yields a "file closed" error
    def _upload(self, filename):
        storage = TestingFileStorage(filename=filename)
        r = self.app.post('/upload', data={'file': storage})
        return r

    def test_upload(self):
        r = self._upload('toto.pdf')
        self.assertEqual(r.status_code, 302)
        m = re.search('/view/(\d+)', r.location)
        self.assertIsNotNone(m)
        docid = m.group(1)
        comm = 'bla bla bla'
        r = self.app.post('/comment/new',
                          data={'docid': docid,
                                'comment': comm
                                })
        self.assertEqual(r.status_code, 302)
        r = self.app.get(r.location)
        self.assertEqual(r.status_code, 200)
        self.assertIn(comm, r.data)

    def test_no_doc(self):
        r = self.app.get('/view/0')
        self.assertEqual(r.status_code, 404)
