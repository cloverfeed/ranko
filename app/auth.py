from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import login_user
from flask.ext.login import LoginManager
from flask.ext.login import logout_user
from flask.ext.wtf import Form
from itsdangerous import URLSafeSerializer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from wtforms import PasswordField
from wtforms import TextField
from wtforms.validators import EqualTo
from wtforms.validators import Required

from models import db
from models import ROLE_GUEST
from models import User

lm = LoginManager()

auth = Blueprint('auth', __name__)


def auth_user(login, password):
    try:
        user = db.session.query(User).filter(User.name == login).one()
    except NoResultFound:
        return None
    db_hash = user.password
    password = password.encode('utf-8')
    db_hash = db_hash.encode('ascii')
    bcrypt = Bcrypt(current_app)
    if bcrypt.check_password_hash(db_hash, password):
        return user
    else:
        return None


class SignupForm(Form):
    """
    Form used in signup
    """
    username = TextField(validators=[Required()])
    password = PasswordField(
        validators=[Required(),
                    EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField(validators=[Required()])


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Sign up a new user
    """
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        if User.query.filter_by(name=username).first() is not None:
            flash('This username is already taken, sorry.')
            return render_template('signup.html', title='Sign up', form=form)
        password = form.password.data
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash('User successfully created')
        login_user(user)
        return redirect(url_for('bp.home'))
    return render_template('signup.html', title='Sign up', form=form)


class LoginForm(Form):
    """
    Form used in login
    """
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log a user in
    """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = auth_user(username, password)
        if user is None:
            flash('Bad login or password')
            return redirect(url_for('.login'))
        login_user(user)
        flash('Logged in')
        return redirect(request.args.get('next') or url_for('bp.home'))
    return render_template('login.html', title='Log in', form=form)


@auth.route('/logout')
def logout():
    """
    Log a user out
    """
    logout_user()
    return redirect(url_for('bp.home'))


def shared_link_serializer():
    salt = 'shared-link'
    serializer = URLSafeSerializer(current_app.secret_key, salt=salt)
    return serializer


def pseudo_user(name, docid):
    user = User.query.filter_by(role=ROLE_GUEST, full_name=name).first()
    if user is None:
        user = User(None, None)
        user.full_name = name
        user.role = ROLE_GUEST
        user.only_doc_id = docid
        db.session.add(user)
        db.session.commit()
    return user
