from flask import Flask
import os
from key import get_secret_key
from uploads import documents
from models import db
from flask.ext.uploads import configure_uploads
from flask.ext.assets import Environment, Bundle
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

def create_app(db_backend=None, testing=False):

    this_dir = os.path.dirname(os.path.abspath(__file__))
    instance_path = os.path.join(this_dir, '..', 'instance')

    app = Flask('Review', instance_path=instance_path)

    app.config['PROPAGATE_EXCEPTIONS'] = True

    app.config['pdfjs_version'] = '1.0.473'

    # CSRF & WTForms
    if testing:
        key_file_name = 'secret-test.key'
    else:
        key_file_name = 'secret.key'
    key_file = os.path.join(app.instance_path, key_file_name)
    app.config['SECRET_KEY'] = get_secret_key(key_file)


    # flask-uploads
    configure_uploads(app, [documents])

    # flask-sqlalchemy
    if db_backend == 'sql_file':
        uri = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    elif db_backend == 'sql_memory':
        uri = 'sqlite://'  # In-memory DB
    else:
        assert False, 'Unknown DB backend: {}'.format(db_backend)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    db.init_app(app)

    # flask-assets
    assets = Environment(app)
    coffee = Bundle(
        'coffee/view.coffee',
        'coffee/selection.coffee',
        'coffee/annotation.coffee',
        'coffee/pdfpage.coffee',
        filters='coffeescript',
        output='gen/app.js'
        )
    assets.register('coffee_app', coffee)

    # flask-migrate
    migrate = Migrate(app, db)

    # flask-script
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    # disable stuff for tests
    if testing:
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['WTF_CSRF_ENABLED'] = False

    from views import bp
    app.register_blueprint(bp)
    assert(len(app.url_map._rules) == 11), app.url_map

    return app
