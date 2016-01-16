import hmac
import json
import sha
from base64 import b64decode
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from time import strptime

from flask import url_for

from common import RankoTestCase


class S3TestCase(RankoTestCase):

    def setUp(self):
        self.app.config['S3_BUCKET'] = 'my-awesome-bucket'
        self.app.config['AWS_SECRET_ACCESS_KEY'] = 'my-awesome-key'

    def test_sign(self):
        r = self.client.get(url_for('s3.sign'))
        params = r.json

        self.assertTrue(params['key'].startswith('uploads/'))

        encoded_policy = params['policy']
        policy = json.loads(b64decode(encoded_policy))
        now = datetime.now()
        expiration = policy['expiration']
        expiration_time = strptime(expiration, '%Y-%m-%dT%H:%M:%S.000Z')
        expiration_datetime = datetime(*expiration_time[:6])
        delta = expiration_datetime - now
        self.assertLess(delta, timedelta(hours=1))

        conditions = policy['conditions']
        self.assertIn({'acl': 'public-read'}, conditions)
        self.assertIn(["starts-with", "$key", "uploads/"], conditions)
        self.assertIn({'bucket': 'my-awesome-bucket'}, conditions)
        self.assertIn({'success_action_status': '201'}, conditions)

        signature = params['signature']
        key = 'my-awesome-key'
        expected = b64encode(hmac.new(key, encoded_policy, sha).digest())
        self.assertEqual(signature, expected)
