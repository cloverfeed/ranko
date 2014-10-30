from flask import Flask
import os
from key import get_secret_key
from uploads import documents
import models
from flask.ext.uploads import configure_uploads
from flask.ext.assets import Environment, Bundle
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

def create_app(config_file=None):

    this_dir = os.path.dirname(os.path.abspath(__file__))
    instance_path = os.path.join(this_dir, '..', 'instance')

    app = Flask('Review', instance_path=instance_path)

    app.config.from_pyfile(os.path.join(this_dir, '..', 'conf/common.py'))

    if config_file:
        app.config.from_pyfile(config_file)

    # CSRF & WTForms
    key_file = os.path.join(app.instance_path, 'secret.key')
    app.config['SECRET_KEY'] = get_secret_key(key_file)

    # flask-uploads
    configure_uploads(app, [documents])

    # flask-sqlalchemy
    if app.config.get('SQLALCHEMY_DATABASE_URI') == '@sql_file':
        here_db = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = here_db
    models.db.init_app(app)

    # flask-assets
    assets = Environment(app)
    coffee = Bundle(
        'coffee/view.coffee',
        'coffee/selection.coffee',
        'coffee/annotation.coffee',
        'coffee/pdfpage.coffee',
        'coffee/upload.coffee',
        filters='coffeescript',
        output='gen/app.js'
        )
    assets.register('coffee_app', coffee)

    # flask-migrate
    migrate = Migrate(app, models.db)

    # flask-admin
    admin = Admin(app, name=app.name + ' Admin')
    admin_models = [models.Document,
                    models.Comment,
                    models.Annotation,
                    ]

    class RestrictedModelView(ModelView):
        def is_accessible(self):
            return True # FIXME when auth is done

    for model in admin_models:
        admin.add_view(RestrictedModelView(model, models.db.session))

    from views import bp
    app.register_blueprint(bp)

    return app
