from factory import create_app
from models import db
import os
from flask.ext.testing import TestCase
from werkzeug import FileStorage
import re
import koremutake
import json


class TestCase(TestCase):
    def create_app(self):
        return create_app(config_file='conf/testing.py')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()

    def test_home(self):
        r = self.client.get('/')
        self.assertIn('Upload and review', r.data)

    # FIXME If called > 1, it yields a "file closed" error
    def _upload(self, filename):
        storage = FileStorage(filename=filename)
        r = self.client.post('/upload', data={'file': storage})
        return r

    def test_upload(self):
        r = self._upload('toto.pdf')
        self.assertStatus(r, 302)
        m = re.search('/view/(\w+)', r.location)
        self.assertIsNotNone(m)
        docid = m.group(1)
        r = self.client.get('/raw/' + docid)
        self.assert200(r)
        self.assertEqual(r.content_type, 'application/pdf')
        comm = 'bla bla bla'
        r = self.client.post('/comment/new',
                          data={'docid': docid,
                                'comment': comm
                                })
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        self.assert200(r)
        self.assertIn(comm, r.data)
        r = self.client.get('/view/' + docid)
        self.assert200(r)
        unkore_docid = str(koremutake.decode(docid))
        r = self.client.get('/view/' + unkore_docid)
        self.assert200(r)

    def test_no_doc(self):
        r = self.client.get('/view/0')
        self.assert404(r)
        r = self.client.get('/raw/0')
        self.assert404(r)

    def test_annotation(self):
        data = { 'doc': 1
               , 'page': 2
               , 'posx': 3
               , 'posy': 4
               , 'width': 5
               , 'height': 6
               , 'value': 'Oh oh'
               }
        r = self.client.post('/annotation/new', data=data)
        self.assert200(r)
        d = json.loads(r.data)
        self.assertIn('id', d)
        id_resp = d['id']

        r = self.client.get('/view/1/annotations')
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
        r = self.client.put('/annotation/{}'.format(id_retr), data=data)
        r = self.client.get('/view/1/annotations')
        d = json.loads(r.data)
        anns = d['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        self.assertEqual(ann['height'], 60)

        r = self.client.delete('/annotation/{}'.format(id_retr))
        self.assert200(r)
        r = self.client.get('/view/1/annotations')
        d = json.loads(r.data)
        self.assertNotIn('2', d['data'])
