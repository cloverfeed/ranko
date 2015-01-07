from app.factory import translate_db_uri
from common import RankoTestCase


class FactoryTestCase(RankoTestCase):
    def test_translate_db_uri(self):
        self.assertEqual(translate_db_uri(self.app, 'sqlite://'), 'sqlite://')
        db_uri = translate_db_uri(self.app, '@sql_file')
        self.assertIn(self.app.instance_path, db_uri)
        self.assertIn('app.db', db_uri)
