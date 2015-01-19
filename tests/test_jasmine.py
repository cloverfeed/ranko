from flask import url_for

from common import RankoTestCase


class JasmineTestCase(RankoTestCase):
    def test_jasmine(self):
        r = self.client.get(url_for('bp.jasmine_tests'))
        self.assert200(r)
