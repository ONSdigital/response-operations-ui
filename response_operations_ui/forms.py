import logging

from response_operations_ui.controllers import collection_exercise_controllers

from flask_wtf import FlaskForm
from structlog import wrap_logger
from wtforms import HiddenField, Label, PasswordField, StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError

logger = wrap_logger(logging.getLogger(__name__))


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
    period = IntegerField('period')
    collection_exercise_id = HiddenField('collection_exercise_id')
    hidden_survey_id = HiddenField('hidden_survey_id')

    @staticmethod
    def validate_period(form, field):
        hidden_survey_id = form.hidden_survey_id.data
        ce_details = collection_exercise_controllers.get_collection_exercises_by_survey(hidden_survey_id)
        inputted_period = field.data
        for key in ce_details:
            if key['exerciseRef'] == inputted_period:
                raise ValidationError('Please enter a period not in use')
            else:
                raise ValidationError('Please enter numbers only for the period')


class ChangeGroupStatusForm(FlaskForm):
    event = StringField('event')
    submit = SubmitField('Confirm')


class CreateCollectionExerciseDetailsForm(FlaskForm):
    user_description = StringField('user_description')
    period = IntegerField('period', validators=[InputRequired(message="Please use numbers only")])
    hidden_survey_id = HiddenField('hidden_survey_id')
    hidden_survey_name = HiddenField('hidden_survey_name')

    @staticmethod
    def validate_period(form, field):
        hidden_survey_id = form.hidden_survey_id.data
        ce_details = collection_exercise_controllers.get_collection_exercises_by_survey(hidden_survey_id)
        inputted_period = field.data
        for key in ce_details:
            if key['exerciseRef'] == inputted_period:
                raise ValidationError('Please enter a period not in use')
            else:
                raise ValidationError('Please enter numbers only for the period')


class EditSurveyDetailsForm(FlaskForm):
    long_name = StringField('long_name')
    short_name = StringField('short_name', validators=[InputRequired(message="Please remove spaces in short name")])
    hidden_survey_ref = HiddenField('hidden_survey_ref')

    @staticmethod
    def validate_short_name(form, field):
        short_name = field.data
        if ' ' in short_name:
            raise ValidationError('Please remove spaces in short name')
