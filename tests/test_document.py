# -*- coding: utf-8 -*-
import re
from io import BytesIO

import koremutake
from flask import url_for
from werkzeug import FileStorage

from app.models import Document
from common import RankoTestCase


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
        r = self._annotate(data)
        self.assert401(r)
        self._login('username', 'password', signup=True)
        r = self._annotate(data)
        self.assert400(r)

        docid = self._new_upload_id('blabla.pdf')
        data['doc'] = docid
        r = self._annotate(data)
        self.assert201(r)
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
            r = self._annotate(bad_data)
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
        r = self.client_put_json('/api/annotation/{}'.format(id_retr), data=data)
        self.assert401(r)

        self._login('username', 'password')
        r = self.client_put_json('/api/annotation/{}'.format(id_retr), data=data)
        self.assert200(r)

        r = self.client.get('/view/{}/annotations'.format(docid))
        anns = r.json['data']['2']
        self.assertEqual(len(anns), 1)
        ann = anns[0]
        self.assertEqual(ann['height'], 60)
        self.assertEqual(ann['state'], 'closed')

        self._login('c', 'c')
        r = self._delete_annotation(id_retr)
        self.assert401(r)

        self._login('username', 'password')
        r = self._delete_annotation(id_retr)
        self.assert204(r)
        r = self.client.get('/view/1/annotations')
        self.assertNotIn('2', r.json['data'])

    def _delete_annotation(self, docid):
        return self.client.delete('/api/annotation/{}'.format(docid))

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

        r = self._edit(docid, {'title': 'New awesome title'})
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        self.assert200(r)
        self.assertIn('New awesome title', r.data)

        r = self.client.get('/')
        self.assert200(r)
        self.assertIn('New awesome title', r.data)

    def _edit(self, docid, data):
        edit_path = '/view/{}/edit'.format(docid)
        return self.client.post(edit_path, data=data)

    def test_delete(self):
        self._login('a', 'b', signup=True)
        r = self._upload('toto.pdf')
        self.assertStatus(r, 302)
        docid = self._extract_docid(r)

        edit_path = '/view/{}/edit'.format(docid)
        r = self.client.get(edit_path)
        self.assert200(r)
        self.assertIn('Delete', r.data)

        r = self._delete(docid)
        self.assertStatus(r, 302)
        r = self.client.get(r.location)
        self.assert200(r)

        view_path = '/view/{}'.format(docid)
        r = self.client.get(view_path)
        self.assert404(r)

    def _delete(self, docid):
        delete_path = '/view/{}/delete'.format(docid)
        return self.client.post(delete_path)

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

    def test_signup_empty(self):
        r = self._signup('', '')
        self.assertIn('This field is required', r.data)

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
        self._login('a', 'b', signup=True)
        docid = self._new_upload_id('toto.pdf')
        r = self._share_link(docid, 'Bob')
        self.assert200(r)
        h = r.json['data']
        self._logout()

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
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('toto.pdf')
        r = self._share_link(docid, 'Ohé')
        self.assert200(r)
        self._logout()
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
        self.assert201(r)

    def _annotate(self, data):
        return self.client_post_json('/api/annotation', data=data)

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
        return r.status_code == 201

    def _can_comment_on(self, docid):
        comm = 'bla bla bla'
        r = self.client.post('/comment/new',
                             data={'docid': docid,
                                   'comment': comm
                                   },
                             follow_redirects=True,
                             )
        return r.status_code == 200

    def test_upload_image(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('x.png')
        r = self.client.get(url_for('bp.home'))
        self.assertIn('glyphicon-picture', r.data)

    def test_detect_unknown(self):
        self.assertRaises(AssertionError, Document.detect_filetype, 'x.txt')

    def test_edit_delete_only_uploader(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('toto.pdf')
        self._logout()
        r = self._delete(docid)
        self.assert401(r)
        r = self._edit(docid, data={"title": "My title"})
        self.assert401(r)

        view_path = '/view/{}'.format(docid)
        r = self.client.get(view_path)
        self.assert200(r)
        self.assertNotIn('Edit', r.data)

    def test_share_only_uploader(self):
        self._login('a', 'a', signup=True)
        docid = self._new_upload_id('toto.pdf')
        self._logout()
        r = self._share_link(docid, 'Bob')
        self.assert401(r)

        view_path = '/view/{}'.format(docid)
        r = self.client.get(view_path)
        self.assert200(r)
        self.assertNotIn('review link', r.data)
