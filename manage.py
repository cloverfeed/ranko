"""
Flask-script stuff
"""
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
from app.factory import create_app

def main():
    manager = Manager(create_app)
    manager.add_command('db', MigrateCommand)
    manager.add_option('-c', '--config', dest='config_file', required=False)

    manager.run()

if __name__ == '__main__':
    main()
