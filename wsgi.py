"""
WSGI callable as called by uwsgi.
Production equivalent of run.py.
"""
from app.factory import create_app

app = create_app(config_file='conf/production.py')
