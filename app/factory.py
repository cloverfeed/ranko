import os

import scss.config
from flask import Flask
from flask import g
from flask import send_from_directory
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.assets import Bundle
from flask.ext.assets import Environment
from flask.ext.login import current_user
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand
from flask.ext.uploads import configure_uploads
from xstatic.main import XStatic

import models
from annotation import annotation
from audio_annotation import audioann
from auth import auth
from auth import lm
from comment import comment
from document import document
from key import get_secret_key
from uploads import documents
from views import bp
from views import page_not_found


def translate_db_uri(app, db_uri):
    if db_uri == '@sql_file':
        here_db = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
        return here_db
    return db_uri


def configure_secret_key(app):
    """
    For CSRF & WTForms.
    """
    key_file = os.path.join(app.instance_path, 'secret.key')
    app.config['SECRET_KEY'] = get_secret_key(key_file)


def configure_ext_uploads(app):
    """
    Configure the flask-uploads extension.
    """
    configure_uploads(app, [documents])


def configure_ext_sqlalchemy(app):
    """
    Configure the flask-sqlalchemy extension.
    """
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_DATABASE_URI'] = translate_db_uri(app, db_uri)
    models.db.init_app(app)


def configure_xstatic(app):
    """
    Configure XStatic assets.
    """
    mod_names = [
        'bootstrap_scss',
        'jquery',
    ]
    pkg = __import__('xstatic.pkg', fromlist=mod_names)
    serve_files = {}
    for mod_name in mod_names:
        mod = getattr(pkg, mod_name)
        xs = XStatic(mod,
                     root_url='/xstatic',
                     provider='local',
                     protocol='http',
                     )
        serve_files[xs.name] = xs.base_dir

    @app.route('/xstatic/<xs_package>/<path:filename>')
    def xstatic(xs_package, filename):
        base_dir = serve_files[xs_package]
        return send_from_directory(base_dir, filename)

    return serve_files


def configure_ext_assets(app, serve_files):
    """
    Configure the flask-assets extension.
    """
    assets = Environment(app)
    coffee = Bundle(
        'coffee/view.coffee',
        'coffee/selection.coffee',
        'coffee/annotation.coffee',
        'coffee/page.coffee',
        'coffee/form.coffee',
        'coffee/listview.coffee',
        'coffee/audioplayer.coffee',
        'coffee/rest.coffee',
        'coffee/flash.coffee',
        filters='coffeescript',
        output='gen/app.js'
        )
    assets.register('coffee_app', coffee)

    scss_bundle = Bundle(
        'scss/bootstrap_custom.scss',
        'scss/view.scss',
        'scss/shame.scss',
        depends='**/*.scss',
        filters='pyscss',
        output='gen/app.css'
        )
    assets.register('scss_all', scss_bundle)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    scss.config.LOAD_PATHS = [
        os.path.join(serve_files['bootstrap_scss'], 'scss'),
        os.path.join(this_dir, '../static/vendor/bootswatch-darkly'),
    ]


def configure_ext_migrate(app):
    """
    Configure the flask-migrate extension.
    """
    migrate = Migrate(app, models.db)


def configure_ext_login(app):
    """
    Configure the flask-login extension.
    """
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


def configure_ext_admin(app):
    """
    Configure the flask-admin extension.
    """
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


def register_blueprints(app):
    blueprints = [
        bp,
        document,
        comment,
        annotation,
        auth,
        audioann,
        ]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def create_app(config_file=None):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    instance_path = os.path.join(this_dir, '..', 'instance')

    app = Flask('Review', instance_path=instance_path)
    app.config.from_pyfile(os.path.join(this_dir, '..', 'conf/common.py'))

    if config_file:
        app.config.from_pyfile(config_file)

    configure_secret_key(app)
    configure_ext_uploads(app)
    configure_ext_sqlalchemy(app)
    serve_files = configure_xstatic(app)
    configure_ext_assets(app, serve_files)
    configure_ext_migrate(app)
    configure_ext_login(app)
    configure_ext_admin(app)

    register_blueprints(app)

    @app.errorhandler(404)
    def handle_404(self):
        return page_not_found()

    return app
