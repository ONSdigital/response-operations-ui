import logging
import re

from flask_wtf import FlaskForm
from structlog import wrap_logger
from wtforms import HiddenField, Label, PasswordField, StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
from response_operations_ui.controllers import survey_controllers

logger = wrap_logger(logging.getLogger(__name__))

survey_ref_validation = re.compile("^[0-9]{1,6}$")

class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired("Please enter a username")])
    password = PasswordField('Password', [InputRequired("Please enter a password")])
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
    hidden_subject = HiddenField('hidden_subject')
    hidden_survey = HiddenField('hidden_survey')
    hidden_survey_id = HiddenField('hidden_survey_id')
    hidden_ru_ref = HiddenField('hidden_ru_ref')
    hidden_business = HiddenField('hidden_business')
    hidden_to = HiddenField('hidden_to')
    hidden_to_uuid = HiddenField('hidden_to_uuid')
    hidden_to_ru_id = HiddenField('hidden_to_ru_id')


class SearchForm(FlaskForm):
    query = StringField('Query')
    submit = SubmitField('Search')


class EditContactDetailsForm(FlaskForm):
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    email = StringField('emailAddress')
    telephone = StringField('telephone')
    hidden_email = HiddenField('hidden_email')

    def __init__(self, form, default_values=None):
        super().__init__(form)
        if default_values:
            self.first_name.data = default_values.get('firstName')
            self.last_name.data = default_values.get('lastName')
            self.email.data = default_values.get('emailAddress')
            self.telephone.data = default_values.get('telephone')


class EditCollectionExerciseDetailsForm(FlaskForm):
    user_description = StringField('user_description')
    period = StringField('period')
    collection_exercise_id = HiddenField('collection_exercise_id')


class ChangeGroupStatusForm(FlaskForm):
    event = StringField('event')
    submit = SubmitField('Confirm')


class EditSurveyDetailsForm(FlaskForm):
    long_name = StringField('long_name')
    short_name = StringField('short_name', validators=[InputRequired(message="Please remove spaces in short name")])
    hidden_survey_ref = HiddenField('hidden_survey_ref')

    @staticmethod
    def validate_short_name(form, field):
        short_name = field.data
        if ' ' in short_name:
            raise ValidationError('Please remove spaces in short name')

class CreateSurveyDetailsForm(FlaskForm):
    legal_basis_list = survey_controllers.get_legal_basis_list()
    long_name = StringField('long_name')
    short_name = StringField('short_name', validators=[InputRequired(message="Please remove spaces in Abbreviation")])
    # MATTTODO implement actual validation
    survey_ref = StringField('survey_ref', validators=[InputRequired(message="Please remove spaces in Survey ID")])
    legal_basis = SelectField('legal_basis', choices=[('','Select an option')] + legal_basis_list)

    @staticmethod
    def validate_short_name(form, field):
        short_name = field.data
        if ' ' in short_name:
            raise ValidationError('Please remove spaces in Abbreviation')

    @staticmethod
    def validate_survey_ref(form, field):
        survey_ref = field.data
        if not survey_ref_validation.match(survey_ref):
            raise ValidationError('The Survey ID should consist of between 1 and 6 digits')

    @staticmethod
    def validate_legal_basis(form, field):
        legal_basis = field.data
        if not legal_basis:
            raise ValidationError('Please select a legal basis')
