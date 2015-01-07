import os

from app.key import get_secret_key
from common import RankoTestCase


class KeyTestCase(RankoTestCase):
    def test_recreate(self):
        secret_key_file = 'test.key'

        self.assertFalse(os.path.isfile(secret_key_file))
        key = get_secret_key(secret_key_file)
        self.assertTrue(os.path.isfile(secret_key_file))

        key2 = get_secret_key(secret_key_file)
        self.assertEqual(key, key2)

        os.unlink(secret_key_file)
