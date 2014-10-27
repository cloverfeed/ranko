"""
Flask-script stuff
"""
from flask.ext.migrate import MigrateCommand, stamp
from flask.ext.script import Manager
from app.factory import create_app
from app.models import db

def main():
    manager = Manager(create_app)
    manager.add_command('db', MigrateCommand)
    manager.add_option('-c', '--config', dest='config_file', required=False)

    @manager.command
    def create():
        "Creates database tables from sqlalchemy models"
        db.create_all()
        stamp()

    manager.run()

if __name__ == '__main__':
    main()
