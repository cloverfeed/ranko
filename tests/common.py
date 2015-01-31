import re
from io import BytesIO

import koremutake
from flask.ext.testing import TestCase
from werkzeug import FileStorage

from app.factory import create_app
from app.models import db


class RankoTestCase(TestCase):
    def create_app(self):
        return create_app(config_file='conf/testing.py')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()

    def _login(self, username, password, signup=False):
        if signup:
            self._signup(username, password)
        return self.client.post('/login', data=dict(
            username=username,
            password=password
            ), follow_redirects=True)

    def _signup(self, username, password):
        return self.client.post('/signup', data=dict(
            username=username,
            password=password,
            confirm=password
            ), follow_redirects=True)

    def _upload(self, filename, title=None, stream=None):
        if stream is None:
            stream = BytesIO()
        storage = FileStorage(filename=filename, stream=stream)
        post_data = {'file': storage}
        if title is not None:
            post_data['title'] = title
        r = self.client.post('/upload', data=post_data)
        return r

    def _new_upload_id(self, filename):
        r = self._upload(filename, title='')
        docid = self._extract_docid(r)
        return koremutake.decode(docid)

    def _extract_docid(self, r):
        m = re.search('/view/(\w+)', r.location)
        self.assertIsNotNone(m)
        docid = m.group(1)
        return docid

    def assert204(self, r):
        self.assertEqual(r.status_code, 204)
