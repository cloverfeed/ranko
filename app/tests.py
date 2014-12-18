import json
import os
import re
from io import BytesIO

import koremutake
from flask import url_for
from flask.ext.testing import TestCase
from werkzeug import FileStorage

from factory import create_app
from models import db


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

    def _upload(self, filename, title=None):
        storage = FileStorage(filename=filename, stream=BytesIO())
        post_data = {'file': storage}
        if title is not None:
            post_data['title'] = title
        r = self.client.post('/upload', data=post_data)
        return r

    def _new_upload_id(self, filename):
        r = self._upload('toto.pdf', title='')
        docid = self._extract_docid(r)
        return koremutake.decode(docid)

    def test_upload(self):
        r = self._login('a', 'a', signup=True)
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
        data = {'doc': 1,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 6,
                'value': 'Oh oh',
                }
        r = self.client.post('/annotation/new', data=data)
        self.assert401(r)
        self._login('username', 'password', signup=True)
        r = self.client.post('/annotation/new', data=data)
        self.assert200(r)
        d = json.loads(r.data)
        self.assertIn('id', d)
        id_resp = d['id']

        bad_data = {'doc': 1,
                    'page': 2,
                    'posx': 3,
                    'posy': 4,
                    'width': 5,
                    'height': 6,
                    'value': 'Oh oh',
                    }
        for key in ['doc', 'page', 'posx', 'posy', 'width', 'height']:
            ok = bad_data[key]
            bad_data[key] = 0.5
            r = self.client.post('/annotation/new', data=bad_data)
            self.assert400(r)
            bad_data[key] = ok

        r = self.client.get('/view/1/annotations')
        d = json.loads(r.data)
        anns = d['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        id_retr = ann['id']
        self.assertEqual(ann['height'], 6)
        self.assertEqual(ann['state'], 'open')
        self.assertEqual(id_retr, id_resp)

        data = {'doc': 1,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 60,
                'value': 'Oh oh',
                'state': 'closed',
                }
        r = self.client.put('/annotation/{}'.format(id_retr), data=data)
        self.assert200(r)
        r = self.client.get('/view/1/annotations')
        d = json.loads(r.data)
        anns = d['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        self.assertEqual(ann['height'], 60)
        self.assertEqual(ann['state'], 'closed')

        r = self.client.delete('/annotation/{}'.format(id_retr))
        self.assert200(r)
        r = self.client.get('/view/1/annotations')
        d = json.loads(r.data)
        self.assertNotIn('2', d['data'])

    def _extract_docid(self, r):
        m = re.search('/view/(\w+)', r.location)
        self.assertIsNotNone(m)
        docid = m.group(1)
        return docid

    def test_upload_rev(self):
        r = self._upload('toto.pdf')
        docid = self._extract_docid(r)
        r = self.client.get(r.location)
        data = {'file': FileStorage(filename='totov2.pdf', stream=BytesIO())}
        r = self.client.post('/upload',
                             data=data,
                             query_string={'revises': docid},
                             )
        self.assertStatus(r, 302)
        m = re.search('/view/(\w+)', r.location)
        self.assertIsNotNone(m)
        docid2 = m.group(1)

        # Check that each rev points to each rev
        for doca in [docid, docid2]:
            r = self.client.get('/view/{}/revisions'.format(doca))
            self.assert200(r)
            for docb in [docid, docid2]:
                self.assertIn(docb, r.data)

    def _signup(self, username, password):
        return self.client.post('/signup', data=dict(
            username=username,
            password=password,
            confirm=password
            ), follow_redirects=True)

    def _login(self, username, password, signup=False):
        if signup:
            self._signup(username, password)
        return self.client.post('/login', data=dict(
            username=username,
            password=password
            ), follow_redirects=True)

    def _logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_signup_login_logout(self):
        r = self.client.get('/')
        self.assertIn('Log in', r.data)
        self.assertNotIn('Log out', r.data)
        self.assertNotIn('Admin panel', r.data)
        r = self._signup('a', 'a')
        self.assertIn('User successfully created', r.data)
        self.assertIn('Signed in as a', r.data)
        self.assertNotIn('Log in', r.data)
        self.assertIn('Log out', r.data)
        self.assertNotIn('Admin panel', r.data)
        r = self._logout()
        self.assertIn('Log in', r.data)
        self.assertNotIn('Log out', r.data)

    def test_login_nonexistent(self):
        r = self._login('doesnt', 'exist')
        self.assertIn('Bad login or password', r.data)

    def test_login_bad_pass(self):
        self._signup('a', 'a')
        r = self._login('a', 'b')
        self.assertIn('Bad login or password', r.data)

    def test_home_logged_in(self):
        self._login('a', 'b', signup=True)
        r = self.client.get('/')
        self.assertNotIn('jumbotron', r.data)  # Jumbotron = landing

    def test_edit_title(self):
        self._login('a', 'b', signup=True)
        r = self._upload('toto.pdf')
        self.assertStatus(r, 302)
        docid = self._extract_docid(r)

        edit_path = '/view/{}/edit'.format(docid)
        r = self.client.get(edit_path)
        self.assert200(r)

        r = self.client.post(edit_path, data={'title': 'New awesome title'})
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        self.assert200(r)
        self.assertIn('New awesome title', r.data)

        r = self.client.get('/')
        self.assert200(r)
        self.assertIn('New awesome title', r.data)

    def test_delete(self):
        self._login('a', 'b', signup=True)
        r = self._upload('toto.pdf')
        self.assertStatus(r, 302)
        docid = self._extract_docid(r)

        edit_path = '/view/{}/edit'.format(docid)
        r = self.client.get(edit_path)
        self.assert200(r)
        self.assertIn('Delete', r.data)

        delete_path = '/view/{}/delete'.format(docid)
        r = self.client.post(delete_path)
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        self.assert200(r)

        view_path = '/view/{}'.format(docid)
        r = self.client.get(view_path)
        self.assert404(r)

    def test_upload_title(self):
        r = self._upload('toto.pdf', title='Batman is great')
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        self.assert200(r)

        self.assertIn('Batman is great', r.data)

    def test_upload_title_blank(self):
        self._login('a', 'b', signup=True)
        r = self._upload('toto.pdf', title='')
        self.assertStatus(r, 302)
        docid = self._extract_docid(r)
        r = self.client.get('/')
        empty_link = "></a>"
        self.assertNotIn(empty_link, r.data)

    def test_signup_twice(self):
        self._signup('a', 'b')
        r = self._signup('a', 'c')
        self.assertIn('already taken', r.data)

    def test_share_link(self):
        docid = self._new_upload_id('toto.pdf')
        data = {'name': 'Bob'}
        r = self.client.post(url_for('bp.share_doc', id=docid), data=data)
        self.assert200(r)
        d = json.loads(r.data)
        self.assertIn('data', d)
        h = d['data']

        h2 = h + 'x'
        r = self.client.get(url_for('bp.view_shared_doc', key=h2))
        self.assertRedirects(r, url_for('bp.home'))

        r = self.client.get(url_for('bp.view_shared_doc', key=h))
        self.assertRedirects(r, url_for('bp.view_doc', id=docid))
        r = self.client.get(r.location)
        self.assertIn('Signed in as Bob (guest)', r.data)

        r = self.client.get(url_for('bp.view_shared_doc', key=h))
        self.assertRedirects(r, url_for('bp.view_doc', id=docid))
        r = self.client.get(r.location)
        self.assertIn('Signed in as Bob (guest)', r.data)

        other_docid = self._new_upload_id('blabla.pdf')

        self.assertTrue(self._can_annotate(docid))
        self.assertFalse(self._can_annotate(other_docid))

        self.assertTrue(self._can_comment_on(docid))
        self.assertFalse(self._can_comment_on(other_docid))

    def _can_annotate(self, docid):
        data = {'doc': docid,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 6,
                'value': 'Oh oh',
                }
        r = self.client.post('/annotation/new', data=data)
        return r.status_code == 200

    def _can_comment_on(self, docid):
        comm = 'bla bla bla'
        r = self.client.post('/comment/new',
                             data={'docid': docid,
                                   'comment': comm
                                   },
                             follow_redirects=True,
                             )
        return r.status_code == 200
