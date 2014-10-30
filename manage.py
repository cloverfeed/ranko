"""
Flask-script stuff
"""
from flask.ext.migrate import MigrateCommand, stamp
from flask.ext.script import Manager
from app.factory import create_app
from app.models import db, User, ROLE_ADMIN
import string
import random

def main():
    manager = Manager(create_app)
    manager.add_command('db', MigrateCommand)
    manager.add_option('-c', '--config', dest='config_file', required=False)

    @manager.command
    def create():
        "Creates database tables from sqlalchemy models"
        db.create_all()
        stamp()

    @manager.command
    def makeadmin():
        "Create an admin user with a random password"
        letters = string.ascii_letters + string.digits
        length = 20
        password = ''.join(random.choice(letters) for _ in range(length))
        user = User('admin', password)
        user.role = ROLE_ADMIN
        db.session.add(user)
        db.session.commit()
        print password

    manager.run()

if __name__ == '__main__':
    main()
