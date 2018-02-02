import logging

from flask_wtf import FlaskForm
from structlog import wrap_logger
from wtforms import PasswordField, StringField, SubmitField, TextAreaField, Label, HiddenField
from wtforms.validators import InputRequired, Length

logger = wrap_logger(logging.getLogger(__name__))


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired("Username is required")])
    password = PasswordField('Password', [InputRequired("Password is required")])
    submit = SubmitField('Sign in')


class SecureMessageForm(FlaskForm):
    send = SubmitField(label='Send')
    subject = StringField('Subject',
                          validators=[InputRequired(message="Please enter a subject"),
                                      Length(max=96, message="Please enter a subject less than 100 characters")])
    body = TextAreaField('Message',
                         validators=[InputRequired(message="Please enter a message"),
                                     Length(max=10000, message="Please enter a subject less than 10000 characters")])
    survey = Label('Survey', text="")
    ru_ref = Label('RU ref', text="")
    business = Label('Business', text="")
    to = Label('To', text="")
    hidden_survey = HiddenField('hidden_survey')
    hidden_ru_ref = HiddenField('hidden_ru_ref')
    hidden_business = HiddenField('hidden_business')
    hidden_to = HiddenField('hidden_to')
