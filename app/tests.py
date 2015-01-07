# -*- coding: utf-8 -*-
import os
import re
from io import BytesIO

import faker
import koremutake
from flask import url_for
from flask.ext.testing import TestCase
from werkzeug import FileStorage

from factory import create_app
from factory import translate_db_uri
from key import get_secret_key
from models import Annotation
from models import Comment
from models import db
from models import Document
from models import ROLE_ADMIN
from models import User


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


class DocTestCase(RankoTestCase):
    def test_home(self):
        r = self.client.get('/')
        self.assertIn('Upload and review', r.data)

    def test_favicon(self):
        r = self.client.get('/favicon.ico', follow_redirects=True)
        self.assert200(r)

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

    def test_upload_bad_ext(self):
        r = self._upload('toto.txt')
        self.assertRedirects(r, url_for('bp.home'))
        r = self.client.get(r.location)
        self.assertIn('Unsupported', r.data)

    def test_no_doc(self):
        r = self.client.get('/view/0')
        self.assert404(r)
        r = self.client.get('/raw/0')
        self.assert404(r)

    def test_annotation(self):
        docid = 1
        data = {'doc': docid,
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
        self.assert400(r)

        docid = self._new_upload_id('blabla.pdf')
        data['doc'] = docid
        r = self.client.post('/annotation/new', data=data)
        self.assert200(r)
        d = r.json
        self.assertIn('id', d)
        id_resp = d['id']

        bad_data = {'doc': docid,
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

        r = self.client.get('/view/{}/annotations'.format(docid))
        anns = r.json['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        id_retr = ann['id']
        self.assertEqual(ann['height'], 6)
        self.assertEqual(ann['state'], 'open')
        self.assertEqual(id_retr, id_resp)

        data = {'doc': docid,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 60,
                'value': 'Oh oh',
                'state': 'closed',
                }
        self._login('c', 'c', signup=True)
        r = self.client.put('/annotation/{}'.format(id_retr), data=data)
        self.assert401(r)

        self._login('username', 'password')
        r = self.client.put('/annotation/{}'.format(id_retr), data=data)
        self.assert200(r)

        r = self.client.get('/view/{}/annotations'.format(docid))
        anns = r.json['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        self.assertEqual(ann['height'], 60)
        self.assertEqual(ann['state'], 'closed')

        self._login('c', 'c')
        r = self._delete(id_retr)
        self.assert401(r)

        self._login('username', 'password')
        r = self._delete(id_retr)
        self.assert200(r)
        r = self.client.get('/view/1/annotations')
        self.assertNotIn('2', r.json['data'])

    def _delete(self, docid):
        return self.client.delete('/annotation/{}'.format(docid))

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

    def test_upload_title_detect(self):
        with open('fixtures/manual.pdf') as f:
            r = self._upload('toto.pdf', title='', stream=f)
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        title = "Hypertext marks in LaTeX: a manual for hyperref"
        self.assertIn(title, r.data)

    def test_signup_twice(self):
        self._signup('a', 'b')
        r = self._signup('a', 'c')
        self.assertIn('already taken', r.data)

    def _share_link(self, docid, name):
        data = {'name': name}
        url = url_for('document.share', id=docid)
        r = self.client.post(url, data=data)
        return r

    def test_share_link(self):
        docid = self._new_upload_id('toto.pdf')
        r = self._share_link(docid, 'Bob')
        self.assert200(r)
        h = r.json['data']

        h2 = h + 'x'
        r = self.client.get(url_for('document.view_shared', key=h2))
        self.assertRedirects(r, url_for('bp.home'))

        r = self.client.get(url_for('document.view_shared', key=h))
        self.assertRedirects(r, url_for('document.view', id=docid))
        r = self.client.get(r.location)
        self.assertIn('Signed in as Bob (guest)', r.data)

        r = self.client.get(url_for('document.view_shared', key=h))
        self.assertRedirects(r, url_for('document.view', id=docid))
        r = self.client.get(r.location)
        self.assertIn('Signed in as Bob (guest)', r.data)

        other_docid = self._new_upload_id('blabla.pdf')

        self.assertTrue(self._can_annotate(docid))
        self.assertFalse(self._can_annotate(other_docid))

        self.assertTrue(self._can_comment_on(docid))
        self.assertFalse(self._can_comment_on(other_docid))

    def test_share_link_unicode(self):
        docid = self._new_upload_id('toto.pdf')
        r = self._share_link(docid, 'Ohé')
        self.assert200(r)
        h = r.json['data']
        url = url_for('document.view_shared', key=h)
        r = self.client.get(url, follow_redirects=True)
        self.assert200(r)

    def test_anon_cant_comment(self):
        docid = self._new_upload_id('bla.pdf')
        self.assertFalse(self._can_comment_on(docid))

    def test_create_annotation_closed(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('bla.pdf')
        data = {'doc': docid,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 6,
                'value': 'Oh oh',
                'state': 'closed',
                }
        r = self._annotate(data)
        self.assert200(r)

    def _annotate(self, data):
        return self.client.post('/annotation/new', data=data)

    def _can_annotate(self, docid):
        data = {'doc': docid,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 6,
                'value': 'Oh oh',
                }
        r = self._annotate(data)
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

    def test_view_list(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('x.pdf')
        data = {'doc': docid,
                'page': 2,
                'posx': 3,
                'posy': 4,
                'width': 5,
                'height': 6,
                'value': 'My annotation',
                }
        r = self._annotate(data)
        self.assert200(r)
        r = self.client.get(url_for('document.view_list', id=docid))
        self.assert200(r)
        self.assertIn('My annotation', r.data)

    def test_upload_image(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('x.png')
        r = self.client.get(url_for('bp.home'))
        self.assertIn('glyphicon-picture', r.data)

    def test_detect_unknown(self):
        self.assertRaises(AssertionError, Document.detect_filetype, 'x.txt')


class AudioAnnotationTestCase(RankoTestCase):
    def test_create_audio_annotation(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('x.mp3')
        data = {'doc': docid,
                'start': 1,
                'length': 2,
                'text': "Bla",
                }
        r = self._audio_annotate(data)
        self.assert200(r)

        d = r.json
        annid = d['id']

        d = self._annotations_for_doc(docid)
        expected_json = {'doc': docid,
                         'start': 1,
                         'length': 2,
                         'text': "Bla",
                         'id': annid,
                         'state': 'open',
                         'user': 1,
                         }
        self.assertEqual(d, {'data': [expected_json]})

        self._login('b', 'b', signup=True)
        data = {'start': 2,
                'length': 3,
                'text': 'toto',
                'state': 'closed',
                }
        r = self._edit(annid, data)
        self.assert401(r)

        r = self._delete(annid)
        self.assert401(r)

        self._login('a', 'a')

        r = self._edit(annid, data)
        self.assert200(r)
        self.assertEqual(r.json, {'status': 'ok'})

        d = self._annotations_for_doc(docid)
        expected_json['start'] = 2
        expected_json['length'] = 3
        expected_json['text'] = 'toto'
        expected_json['state'] = 'closed'
        self.assertEqual(d, {'data': [expected_json]})

        r = self._delete(annid)
        self.assert200(r)
        self.assertEqual(r.json, {'status': 'ok'})

        d = self._annotations_for_doc(docid)
        self.assertEqual(d, {'data': []})

    def _audio_annotate(self, data):
        return self.client.post(url_for('audioann.audioann_new'), data=data)

    def _annotations_for_doc(self, docid):
        url = url_for('audioann.audio_annotations_for_doc', id=docid)
        r = self.client.get(url)
        self.assert200(r)
        return r.json

    def _edit(self, annid, data):
        url = url_for('audioann.audio_annotation_edit', id=annid)
        return self.client.put(url, data=data)

    def _delete(self, annid):
        url = url_for('audioann.annotation_delete', id=annid)
        return self.client.delete(url)

    def test_view_list_audio(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('x.mp3')
        data = {'doc': docid,
                'start': 2,
                'length': 3,
                'text': 'My annotation',
                }
        r = self._audio_annotate(data)
        self.assert200(r)
        r = self.client.get(url_for('document.view_list', id=docid))
        self.assert200(r)
        self.assertIn('My annotation', r.data)


class KeyTestCase(RankoTestCase):
    def test_recreate(self):
        secret_key_file = 'test.key'

        self.assertFalse(os.path.isfile(secret_key_file))
        key = get_secret_key(secret_key_file)
        self.assertTrue(os.path.isfile(secret_key_file))

        key2 = get_secret_key(secret_key_file)
        self.assertEqual(key, key2)

        os.unlink(secret_key_file)


class FakeTestCase(RankoTestCase):
    def test_generate_models(self):
        fake = faker.Faker()
        user = User.generate(fake)
        doc = Document.generate('pdfdata')
        comm = Comment.generate(fake, doc)
        ann = Annotation.generate(fake, doc, user)


class AdminTestCase(RankoTestCase):
    def test_admin_unauthorized_guest(self):
        self.assertFalse(self._can_see_admin_panel())

    def test_admin_unauthorized_user(self):
        self._login('a', 'a', signup=True)
        self.assertFalse(self._can_see_admin_panel())

    def test_admin_authorized_admin(self):
        self._login('a', 'a', signup=True)
        user = User.query.one()
        user.role = ROLE_ADMIN
        self.assertTrue(self._can_see_admin_panel())

    def _can_see_admin_panel(self):
        r = self.client.get('/admin/')
        self.assert200(r)
        return 'Document' in r.data


class FactoryTestCase(RankoTestCase):
    def test_translate_db_uri(self):
        self.assertEqual(translate_db_uri(self.app, 'sqlite://'), 'sqlite://')
        db_uri = translate_db_uri(self.app, '@sql_file')
        self.assertIn(self.app.instance_path, db_uri)
        self.assertIn('app.db', db_uri)


class ErrorPagesTestCase(RankoTestCase):
    def test_404(self):
        r = self.client.get('/nonexistent')
        self.assertIn('does not exist', r.data)
