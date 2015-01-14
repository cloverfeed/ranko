import os

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://ranko:@/ranko'
SLACK_API_TOKEN = os.getenv('SLACK_API_TOKEN')
SLACK_CHANNEL = '#general'
SLACK_USERNAME = 'Ranko logger'
SLACK_ICON_URL = 'https://i.imgur.com/QxAyIvW.jpg'
