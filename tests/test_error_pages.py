from common import RankoTestCase


class ErrorPagesTestCase(RankoTestCase):
    def test_404(self):
        r = self.client.get('/nonexistent')
        self.assertIn('does not exist', r.data)

    def test_502(self):
        #  This error page cannot be tested with an exception so we rely on the
        #  exposed endpoint that is used by nginx.
        r = self.client.get('/502')
        self.assertIn('Sorry for the inconvenience', r.data)
