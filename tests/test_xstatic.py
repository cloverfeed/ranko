from flask import url_for

from common import RankoTestCase


class XStaticTestCase(RankoTestCase):
    def test_jquery(self):
        url = url_for('xstatic', xs_package='jquery', filename='jquery.min.js')
        r = self.client.get(url)
        self.assert200(r)
        self.assertIn('/*! jQuery v', r.data)
