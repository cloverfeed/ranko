"""
Flask-script stuff
"""
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
from app.factory import create_app

def main():
    app = create_app(db_backend='sql_file')
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    manager.run()

if __name__ == '__main__':
    main()
