import os

from flask import Flask
from flask import g
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.assets import Bundle
from flask.ext.assets import Environment
from flask.ext.login import current_user
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand
from flask.ext.uploads import configure_uploads

import models
from auth import lm
from key import get_secret_key
from uploads import documents


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
        'coffee/page.coffee',
        'coffee/upload.coffee',
        'coffee/listview.coffee',
        'coffee/audioplayer.coffee',
        filters='coffeescript',
        output='gen/app.js'
        )
    assets.register('coffee_app', coffee)

    # flask-migrate
    migrate = Migrate(app, models.db)

    # auth
    lm.init_app(app)

    @lm.user_loader
    def load_user(userid):
        """
        Needed for flask-login.
        """
        return models.User.query.get(int(userid))

    @app.before_request
    def set_g_user():
        g.user = current_user

    # flask-admin
    admin = Admin(app, name=app.name + ' Admin')
    admin_models = [models.User,
                    models.Document,
                    models.Comment,
                    models.Annotation,
                    ]

    class RestrictedModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated() and current_user.is_admin()

    for model in admin_models:
        admin.add_view(RestrictedModelView(model, models.db.session))

    from views import bp
    app.register_blueprint(bp)
    from auth import auth
    app.register_blueprint(auth)

    return app
