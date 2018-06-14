import calendar
import logging
import re

from flask_wtf import FlaskForm
from structlog import wrap_logger

from wtforms import HiddenField, Label, PasswordField, StringField,\
    SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError

from response_operations_ui.controllers import collection_exercise_controllers
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
    period = IntegerField('period')
    collection_exercise_id = HiddenField('collection_exercise_id')
    hidden_survey_id = HiddenField('hidden_survey_id')

    @staticmethod
    def validate_period(form, field):
        hidden_survey_id = form.hidden_survey_id.data
        ce_details = collection_exercise_controllers.get_collection_exercises_by_survey(hidden_survey_id)
        inputted_period = field.data
        if inputted_period is None:
            raise ValidationError('Please enter numbers only for the period')
        for ce in ce_details:
            if ce['exerciseRef'] == str(inputted_period):
                raise ValidationError('Please enter a period not in use')


class ChangeGroupStatusForm(FlaskForm):
    event = StringField('event')
    submit = SubmitField('Confirm')


class EventDateForm(FlaskForm):
    day = StringField('day',
                      validators=[InputRequired(message="Please enter day"),
                                  Length(min=1, max=2, message="Please enter a one or two digit number")])

    MONTHS = [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')]
    month = SelectField('month', choices=MONTHS)

    year = StringField('year',
                       validators=[InputRequired(message="Please enter year"),
                                   Length(min=4, max=4, message="Please enter a 4 digit number")])

    HOURS = [(hour, hour) for hour in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                                       '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']]
    hour = SelectField('hours', choices=HOURS, default='07')

    MINUTES = [('00', '00'), ('15', '15'), ('30', '30'), ('45', '45')]
    minute = SelectField('minutes', choices=MINUTES, default='00')
    submit = SubmitField('Save')

    def validate_day(form, field):
        days_in_month = calendar.monthrange(int(form.year.data), int(form.month.data))[1]
        if int(field.data) < 1 or int(field.data) > days_in_month:
            raise ValidationError('Day out of range for month')


class CreateCollectionExerciseDetailsForm(FlaskForm):
    user_description = StringField('user_description')
    period = IntegerField('period')
    hidden_survey_id = HiddenField('hidden_survey_id')
    hidden_survey_name = HiddenField('hidden_survey_name')

    @staticmethod
    def validate_period(form, field):
        inputted_period = field.data
        if inputted_period is None:
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


class CreateSurveyDetailsForm(FlaskForm):
    long_name = StringField('long_name')
    short_name = StringField('short_name', validators=[InputRequired(message="Please remove spaces in Abbreviation")])
    survey_ref = StringField('survey_ref', validators=[InputRequired(message="Please remove spaces in Survey ID")])
    legal_basis = SelectField('legal_basis', choices=[('', 'Select an option')])

    def __init__(self, form):
        super().__init__(form)
        self.legal_basis.choices = [('', 'Select an option')] + survey_controllers.get_legal_basis_list()

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


class RemoveLoadedSample(FlaskForm):
    period = StringField('period')
    short_name = StringField('short_name')
