from flask import url_for

from common import RankoTestCase


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
