import hmac
import json
import sha
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

from flask import Blueprint
from flask import current_app
from flask import jsonify

s3 = Blueprint('s3', __name__)


def make_policy():
    bucket = current_app.config.get('S3_BUCKET')
    assert bucket is not None, "S3 upload is not configured"
    now = datetime.now()
    delta = timedelta(hours=1)
    expiration = (now + delta).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    conditions = [{'bucket': bucket},
                  {'acl': 'public-read'},
                  ["starts-with", "$key", "uploads/"],
                  {'success_action_status': '201'},
                  ]
    policy = {'expiration': expiration,
              'conditions': conditions,
              }
    return b64encode(json.dumps(policy).replace('\n', '').replace('\r', ''))


def sign_policy(policy):
    key = current_app.config.get('AWS_SECRET_ACCESS_KEY')
    assert key is not None, "S3 upload is not configured"
    return b64encode(hmac.new(key, policy, sha).digest())


@s3.route('/s3_sign')
def sign():
    key = "uploads/" + uuid4().hex
    policy = make_policy()
    signature = sign_policy(policy)
    return jsonify(key=key, policy=policy, signature=signature)
