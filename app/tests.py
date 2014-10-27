from app import app, db
from .key import get_secret_key
import unittest
import os
from flask.ext.testing import TestCase
from flask.ext.uploads import TestingFileStorage
import re
import koremutake
import json


class TestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['WTF_CSRF_ENABLED'] = False

        uri = 'sqlite://'  # In-memory DB
        app.config['SQLALCHEMY_DATABASE_URI'] = uri

        self.key_file = os.path.join(app.instance_path, 'secret-test.key')
        app.config['SECRET_KEY'] = get_secret_key(self.key_file)

        return app

    def setUp(self):
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
        m = re.search('/view/(\w+)', r.location)
        self.assertIsNotNone(m)
        docid = m.group(1)
        r = self.app.get('/raw/' + docid)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content_type, 'application/pdf')
        comm = 'bla bla bla'
        r = self.app.post('/comment/new',
                          data={'docid': docid,
                                'comment': comm
                                })
        self.assertEqual(r.status_code, 302)
        r = self.app.get(r.location)
        self.assertEqual(r.status_code, 200)
        self.assertIn(comm, r.data)
        r = self.app.get('/view/' + docid)
        self.assertEqual(r.status_code, 200)
        unkore_docid = str(koremutake.decode(docid))
        r = self.app.get('/view/' + unkore_docid)
        self.assertEqual(r.status_code, 200)

    def test_no_doc(self):
        r = self.app.get('/view/0')
        self.assertEqual(r.status_code, 404)
        r = self.app.get('/raw/0')
        self.assertEqual(r.status_code, 404)

    def test_annotation(self):
        data = { 'doc': 1
               , 'page': 2
               , 'posx': 3
               , 'posy': 4
               , 'width': 5
               , 'height': 6
               , 'value': 'Oh oh'
               }
        r = self.app.post('/annotation/new', data=data)
        self.assertEqual(r.status_code, 200)
        d = json.loads(r.data)
        self.assertIn('id', d)
        id_resp = d['id']

        r = self.app.get('/view/1/annotations')
        d = json.loads(r.data)
        anns = d['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        id_retr = ann['id']
        self.assertEqual(ann['height'], 6)
        self.assertEqual(id_retr, id_resp)

        data = { 'doc': 1
               , 'page': 2
               , 'posx': 3
               , 'posy': 4
               , 'width': 5
               , 'height': 60
               , 'value': 'Oh oh'
               }
        r = self.app.put('/annotation/{}'.format(id_retr), data=data)
        r = self.app.get('/view/1/annotations')
        d = json.loads(r.data)
        anns = d['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        self.assertEqual(ann['height'], 60)

        r = self.app.delete('/annotation/{}'.format(id_retr))
        self.assertEqual(r.status_code, 200)
        r = self.app.get('/view/1/annotations')
        d = json.loads(r.data)
        self.assertNotIn('2', d['data'])
