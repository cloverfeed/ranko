"""
WSGI callable as called by uwsgi.
Production equivalent of run.py.
"""
from app.factory import create_app

app = create_app(db_backend='sql_file')
