import logging
import enum

from flask_wtf import FlaskForm
from structlog import wrap_logger
from wtforms import HiddenField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, EqualTo, Length, DataRequired, Email, ValidationError

from response_operations_ui import app


logger = wrap_logger(logging.getLogger(__name__))


class EnrolmentCodeForm(FlaskForm):
    enrolment_code = StringField('Enrolment Code', [InputRequired()])


class RegistrationForm(FlaskForm):
    first_name = StringField('First name',
                             validators=[InputRequired("First name is required"),
                                         Length(max=254,
                                                message='Your first name must be less than 254 characters')])

    last_name = StringField('Last name',
                            validators=[InputRequired("Last name is required"),
                                        Length(max=254, message='Your last name must be less than 254 characters')])

    email_address = StringField('Enter your email address',
                                validators=[InputRequired("Email address is required"),
                                            Email(message="Your email should be of the form 'myname@email.com' "),
                                            Length(max=254,
                                                   message='Your email must be less than 254 characters')])

    password = PasswordField('Create a password',
                             validators=[DataRequired("Password is required"),
                                         EqualTo('password_confirm', message=app.config['PASSWORD_MATCH_ERROR_TEXT']),
                                         Length(min=app.config['PASSWORD_MIN_LENGTH'],
                                                max=app.config['PASSWORD_MAX_LENGTH'],
                                                message=app.config['PASSWORD_CRITERIA_ERROR_TEXT'])])
    password_confirm = PasswordField('Re-type your password')

    enrolment_code = HiddenField('Enrolment Code')

    @staticmethod
    def validate_password(form, field):
        password = field.data
        if password.isalnum() or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            raise ValidationError(app.config['PASSWORD_CRITERIA_ERROR_TEXT'])


class LoginForm(FlaskForm):
    username = StringField('Email Address', [InputRequired("Email Address is required"),
                                             Email("Your email should be of the form 'myname@email.com' ")])
    password = PasswordField('Password', [InputRequired("Password is required")])


class ForgotPasswordForm(FlaskForm):
    email_address = StringField('Enter your email address',
                                validators=[InputRequired("Email address is required"),
                                            Email(message="Your email should be of the form 'myname@email.com' "),
                                            Length(max=254,
                                                   message='Your email must be less than 254 characters')])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password',
                             validators=[DataRequired("Password is required"),
                                         EqualTo('password_confirm', message=app.config['PASSWORD_MATCH_ERROR_TEXT']),
                                         Length(min=app.config['PASSWORD_MIN_LENGTH'],
                                                max=app.config['PASSWORD_MAX_LENGTH'],
                                                message=app.config['PASSWORD_CRITERIA_ERROR_TEXT'])])
    password_confirm = PasswordField('Re-type new password')

    @staticmethod
    def validate_password(form, field):
        password = field.data
        if password.isalnum() or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            raise ValidationError(app.config['PASSWORD_CRITERIA_ERROR_TEXT'])


class SecureMessagingForm(FlaskForm):
    save_draft = SubmitField(label='Save Draft')
    send = SubmitField(label='Send')
    subject = StringField('Subject')
    body = TextAreaField('Message')
    thread_message_id = HiddenField('Thread message id')
    msg_id = HiddenField('Message id')
    thread_id = HiddenField('Thread id')
    hidden_subject = HiddenField('Hidden Subject')

    @staticmethod
    def validate_subject(form, field):
        subject = form['hidden_subject'].data if form['hidden_subject'].data else field.data
        if len(subject) > 96:
            raise ValidationError('Subject field length must not be greater than 100')
        if form.send.data and not subject:
            raise ValidationError('Please enter a subject')

    @staticmethod
    def validate_body(form, field):
        body = field.data
        if len(body) > 10000:
            raise ValidationError('Body field length must not be greater than 10000')
        if form.send.data and not body:
            raise ValidationError('Please enter a message')


class RespondentStatus(enum.IntEnum):
    CREATED = 0
    ACTIVE = 1
    SUSPENDED = 2
