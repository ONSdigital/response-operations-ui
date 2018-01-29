import logging

from flask_wtf import FlaskForm
from structlog import wrap_logger
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired


logger = wrap_logger(logging.getLogger(__name__))


class LoginForm(FlaskForm):
    user_id = StringField('user_id')
    username = StringField('Username', [InputRequired("Username is required")])
    password = PasswordField('Password', [InputRequired("Password is required")])
    submit = SubmitField('Sign in')
