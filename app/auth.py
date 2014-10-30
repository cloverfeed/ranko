from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask.ext.login import LoginManager, login_user, logout_user
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required, EqualTo
from models import db, User
import bcrypt
from sqlalchemy.orm.exc import NoResultFound

lm = LoginManager()

auth = Blueprint('auth', __name__)


def auth_user(login, password):
    try:
        user = db.session.query(User).filter(User.name == login).one()
    except NoResultFound:
        return None
    db_hash = user.password
    hashed = bcrypt.hashpw(password.encode('utf-8'), db_hash.encode('ascii'))
    if db_hash != hashed:
        return None
    return user


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
        password = form.password.data
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash('User successfully created')
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
