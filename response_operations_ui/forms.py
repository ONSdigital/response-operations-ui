import calendar
import logging
import re

from flask_wtf import FlaskForm
from structlog import wrap_logger
from wtforms import (
    BooleanField,
    EmailField,
    HiddenField,
    IntegerField,
    Label,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    Regexp,
    ValidationError,
)

from response_operations_ui.controllers import (
    collection_exercise_controllers,
    survey_controllers,
)

logger = wrap_logger(logging.getLogger(__name__))

survey_ref_validation = re.compile("^[0-9]{1,6}$")


class LoginForm(FlaskForm):
    username = StringField("Username", [InputRequired("Please enter a username")])
    password = PasswordField("Password", [InputRequired("Please enter a password")])
    submit = SubmitField("Sign in")


class EditUserGroupsForm(FlaskForm):
    surveys_edit = BooleanField()
    surveys_delete = BooleanField()
    reporting_units_edit = BooleanField()
    respondents_edit = BooleanField()
    respondents_delete = BooleanField()
    messages_edit = BooleanField()
    users_admin = BooleanField()


class SecureMessageForm(FlaskForm):
    send = SubmitField(label="Send")
    subject = StringField(
        "Subject",
        validators=[
            InputRequired(message="Please enter a subject"),
            Length(max=96, message="Please enter a subject less than 100 characters"),
        ],
    )
    body = TextAreaField(
        "Message",
        validators=[
            InputRequired(message="Please enter a message"),
            Length(max=50000, message="Please enter a message less than 50000 characters"),
        ],
    )
    survey_id = Label("Survey", text="")
    ru_ref = Label("RU ref", text="")
    business = Label("Business", text="")
    to = Label("To", text="")
    hidden_subject = HiddenField("hidden_subject")
    hidden_survey = HiddenField("hidden_survey")
    hidden_survey_id = HiddenField("hidden_survey_id")
    hidden_ru_ref = HiddenField("hidden_ru_ref")
    hidden_business = HiddenField("hidden_business")
    hidden_to = HiddenField("hidden_to")
    hidden_to_uuid = HiddenField("hidden_to_uuid")
    hidden_to_business_id = HiddenField("hidden_to_business_id")


class SecureMessageRuFilterForm(FlaskForm):
    ru_ref_filter = StringField(
        "ru_ref_filter", validators=[Length(min=11, max=11, message="Ru ref must be 11 characters")]
    )
    submit = SubmitField("Filter")


class UserSearchForm(FlaskForm):
    def strip_whitespace(s):
        if isinstance(s, str):
            s = s.strip()
        return s

    user_search = StringField(
        "user_search",
        validators=[
            InputRequired(message="Please enter a valid email for search"),
            Email(message="The email address must be in the correct format"),
            Length(max=254, message="Your email search is not valid"),
        ],
        filters=[strip_whitespace],
    )
    submit = SubmitField("Filter")


class RespondentSearchForm(FlaskForm):
    first_name = StringField("first_name")
    last_name = StringField("last_name")
    email_address = StringField("email_address")
    page = HiddenField("page")
    submit = SubmitField("Search")

    def validate(form):
        first_name = form.first_name.data or ""
        last_name = form.last_name.data or ""
        email_address = form.email_address.data or ""

        if not (first_name or last_name or email_address):
            return False
        return True


class RuSearchForm(FlaskForm):
    query = StringField("Query")
    submit = SubmitField("Search")


class EditContactDetailsForm(FlaskForm):
    def strip_whitespace(s):
        if isinstance(s, str):
            s = s.strip()
        return s

    last_name = StringField(
        "last_name",
        validators=[
            InputRequired(message="Enter a last name"),
            Length(max=254, message="Last name must be fewer than 254 characters"),
        ],
    )
    first_name = StringField(
        "first_name",
        validators=[
            InputRequired(message="Enter a first name"),
            Length(max=254, message="First name must be fewer than 254 characters"),
        ],
    )
    email = StringField(
        "emailAddress",
        validators=[
            InputRequired("Enter an email address"),
            Email(message="The email address must be in the correct format"),
            Length(max=254, message="Your email must be less than 254 characters"),
        ],
        filters=[strip_whitespace],
    )
    telephone = StringField("telephone", validators=[InputRequired(message="Enter a phone number")])
    hidden_email = HiddenField("hidden_email")

    def __init__(self, form, default_values=None):
        super().__init__(form)
        if default_values:
            self.first_name.data = default_values.get("firstName")
            self.last_name.data = default_values.get("lastName")
            self.email.data = default_values.get("emailAddress")
            self.telephone.data = default_values.get("telephone")


class EditCollectionExerciseDetailsForm(FlaskForm):
    user_description = HiddenField("user_description")
    period = IntegerField("period")
    collection_exercise_id = HiddenField("collection_exercise_id")
    hidden_survey_id = HiddenField("hidden_survey_id")

    @staticmethod
    def validate_period(form, field):
        hidden_survey_id = form.hidden_survey_id.data
        hidden_ce_id = form.collection_exercise_id.data
        ce_details = collection_exercise_controllers.get_collection_exercises_by_survey(hidden_survey_id)
        inputted_period = field.data
        if inputted_period is None:
            raise ValidationError("Please enter numbers only for the period")
        for ce in ce_details:
            if ce["id"] == str(hidden_ce_id):
                continue
            if ce["exerciseRef"] == str(inputted_period):
                raise ValidationError("Please enter a period not in use")


class ChangeGroupStatusForm(FlaskForm):
    event = StringField("event")
    submit = SubmitField("Confirm")


class EventDateForm(FlaskForm):
    day = StringField(
        "day",
        validators=[
            InputRequired(message="Please enter day"),
            Length(min=1, max=2, message="Please enter a one or two digit number"),
        ],
    )

    MONTHS = [
        ("01", "January"),
        ("02", "February"),
        ("03", "March"),
        ("04", "April"),
        ("05", "May"),
        ("06", "June"),
        ("07", "July"),
        ("08", "August"),
        ("09", "September"),
        ("10", "October"),
        ("11", "November"),
        ("12", "December"),
    ]
    month = SelectField("month", choices=MONTHS)

    year = StringField(
        "year",
        validators=[
            InputRequired(message="Please enter year"),
            Length(min=4, max=4, message="Please enter a 4 digit number"),
        ],
    )

    HOURS = [
        (hour, hour)
        for hour in [
            "00",
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
        ]
    ]
    hour = SelectField("hours", choices=HOURS, default="07")

    MINUTES = [("00", "00"), ("15", "15"), ("30", "30"), ("45", "45")]
    minute = SelectField("minutes", choices=MINUTES, default="00")
    checkbox = BooleanField("Agree?")
    submit = SubmitField("Save")

    def validate_day(form, field):
        days_in_month = calendar.monthrange(int(form.year.data), int(form.month.data))[1]
        if int(field.data) < 1 or int(field.data) > days_in_month:
            raise ValidationError("Day out of range for month")


class CreateCollectionExerciseDetailsForm(FlaskForm):
    user_description = StringField("user_description")
    period = IntegerField("period")

    @staticmethod
    def validate_period(form, field):
        inputted_period = field.data
        if inputted_period is None:
            raise ValidationError("Please enter numbers only for the period")


class EditSurveyDetailsForm(FlaskForm):
    long_name = StringField(
        "long_name",
        # Letters, numbers, and (escaped) dash, apostrophe, parentheses, and colon
        validators=[Regexp(regex=r"^[a-zA-Z0-9 \-\'\(\):]+$", message="Please use alphanumeric characters.")],
    )
    short_name = StringField(
        "short_name",
        validators=[
            InputRequired(message="Please remove spaces in short name"),
            Regexp(regex=r"^[a-zA-Z0-9]+$", message="Please use alphanumeric characters only."),
        ],
    )
    survey_mode = StringField()
    hidden_survey_ref = HiddenField("hidden_survey_ref")

    @staticmethod
    def validate_short_name(form, field):
        short_name = field.data
        if " " in short_name:
            raise ValidationError("Please remove spaces in short name")


class ChangeThreadCategoryForm(FlaskForm):
    # These aren't string fields in the html form but the data this form is populated with are strings
    category = StringField(validators=[InputRequired("Please select a category")])
    select_survey = StringField()

    @staticmethod
    def validate_select_survey(form, field):
        if form.category.data == "SURVEY" and not field.data:
            raise ValidationError("Please select a specific survey for this thread")


class CreateSurveyDetailsForm(FlaskForm):
    long_name = StringField(
        "long_name", validators=[Regexp(regex=r"^[a-zA-Z0-9 \-]+$", message="Please use alphanumeric characters only.")]
    )
    short_name = StringField(
        "short_name",
        validators=[
            InputRequired(message="Please remove spaces in Abbreviation"),
            Regexp(regex=r"^[a-zA-Z0-9]+$", message="Please use alphanumeric characters only."),
        ],
    )
    survey_ref = StringField("survey_ref", validators=[InputRequired(message="Please remove spaces in Survey ID")])
    legal_basis = StringField(validators=[InputRequired("Please select a Legal Basis")])
    survey_mode = StringField(validators=[InputRequired("Please select a Survey Mode")])

    def __init__(self, form):
        super().__init__(form)
        self.legal_basis = survey_controllers.get_legal_basis_list()

    @staticmethod
    def validate_short_name(form, field):
        short_name = field.data
        if " " in short_name:
            raise ValidationError("Please remove spaces in Abbreviation")

    @staticmethod
    def validate_survey_ref(form, field):
        survey_ref = field.data
        if not survey_ref_validation.match(survey_ref):
            raise ValidationError("The Survey ID should consist of between 1 and 6 digits")

    @staticmethod
    def validate_legal_basis(form, field):
        legal_basis = field.data
        if not legal_basis:
            raise ValidationError("Please select a legal basis")

    @staticmethod
    def validate_survey_mode(form, field):
        survey_mode = field.data
        if not survey_mode:
            raise ValidationError("Please select EQ, SEFT or EQ AND SEFT")


class LinkCollectionInstrumentForm(FlaskForm):
    formtype = StringField(
        "formtype",
        default="",
        validators=[
            InputRequired(message="Add a 4 digit number"),
            Regexp(regex=r"^[0-9]+$", message="Add a 4 digit number"),
            Length(min=4, max=4, message="Add a 4 digit number"),
        ],
    )


class RemoveLoadedSample(FlaskForm):
    period = StringField("period")
    short_name = StringField("short_name")


class ForgotPasswordForm(FlaskForm):
    email_address = StringField(
        "Enter your email address",
        validators=[
            InputRequired("Email address is required"),
            Email(message="Invalid email address"),
            Length(max=254, message="Your email must be less than 254 characters"),
        ],
    )

    @staticmethod
    def validate_email_address(_, field):
        email = field.data
        return _validate_email_address(email)


def _validate_email_address(email: str):
    """
    Validates an email address, using regex to conform to GDS standards.

    :param field:  Field containing email address for validation.
    """
    local_part, domain_part = email.rsplit("@", 1)
    logger.info("Checking if the email address contains a space or quotes in the local part")
    # this extends the email validator to check if there is whitespace in the email or quotes surrounding local part
    if " " in email:
        logger.info("Space found in email address")
        raise ValidationError("Invalid email address")
    if local_part.startswith('"') and local_part.endswith('"'):
        logger.info("Quotes found in local part of email")
        raise ValidationError("Invalid email address")


class CreateAccountWithPermissionsForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(message="First name is required")])
    last_name = StringField("Last name", validators=[DataRequired(message="Last name is required")])
    email = EmailField("Email", validators=[DataRequired(message="Email is required")])

    surveys_edit = BooleanField()
    surveys_delete = BooleanField()
    reporting_units_edit = BooleanField()
    respondents_edit = BooleanField()
    respondents_delete = BooleanField()
    messages_edit = BooleanField()
    users_admin = BooleanField()

    @staticmethod
    def get_uaa_permission_groups():
        return [
            "surveys_edit",
            "surveys_delete",
            "reporting_units_edit",
            "respondents_edit",
            "respondents_delete",
            "messages_edit",
            "users_admin",
        ]

    @staticmethod
    def validate_email(_, field):
        email = field.data
        _validate_email_address(email)
        local_part, domain_part = email.rsplit("@", 1)
        if domain_part not in ["ons.gov.uk", "ext.ons.gov.uk", "ons.fake"]:
            logger.info("Account requested for non-ONS email address")
            raise ValidationError("Not a valid ONS email address")


class SetAccountPasswordForm(FlaskForm):
    password = PasswordField(
        "Create a new password",
        validators=[
            DataRequired("Your new password is required"),
        ],
    )
    password_confirm = PasswordField(
        "Re-type your new password",
        validators=[
            DataRequired("Re-type your new password"),
            EqualTo("password", message="Enter passwords that match"),
        ],
    )

    @staticmethod
    def validate_password(form, field):
        password = field.data
        if (
            password.isalnum()
            or not any(char.isupper() for char in password)
            or not any(char.isdigit() for char in password)
            or len(password) < 12
            or len(password) > 160
        ):
            raise ValidationError("Enter a password in the correct format")


class ChangeAccountName(FlaskForm):
    first_name = StringField(
        "First name",
        validators=[
            DataRequired("First name is required"),
            Length(max=255, message="Your first name must be less than 255 characters"),
        ],
    )
    last_name = StringField(
        "Last name",
        validators=[
            DataRequired("Last name is required"),
            Length(max=255, message="Your last name must be less than 255 characters"),
        ],
    )


class ChangeEmailForm(FlaskForm):
    email_address = StringField(
        "Enter the ONS email address to create an account for",
        validators=[
            InputRequired("Enter an email address"),
            Email(message="Invalid email address"),
            EqualTo("email_confirm", message="Your emails do not match"),
            Length(max=255, message="Your email must be less than 255 characters"),
        ],
    )

    email_confirm = StringField(
        "Enter the ONS email address to create an account for",
        validators=[
            InputRequired("Enter an email address"),
            EqualTo("email_address", message="Your emails do not match"),
        ],
    )

    @staticmethod
    def validate_email_address(_, field):
        email = field.data
        _validate_email_address(email)
        local_part, domain_part = email.rsplit("@", 1)
        if domain_part not in ["ons.gov.uk", "ext.ons.gov.uk", "ons.fake"]:
            logger.info("Account requested for non-ONS email address")
            raise ValidationError("Not a valid ONS email address")


class BannerCreateForm(FlaskForm):
    title = StringField("Banner title", validators=[InputRequired("Enter a banner title")])
    banner_text = StringField(
        "Banner text",
        validators=[
            InputRequired("Banner text is missing"),
            Length(max=50000, message="Text must be less than 50000 characters"),
        ],
    )


class BannerDeleteForm(FlaskForm):
    delete = BooleanField("Delete banner", default=False)


class BannerPublishForm(FlaskForm):
    banner_text = StringField("Banner text", validators=[InputRequired("Banner text is missing")])


class BannerManageForm(FlaskForm):
    template_id = StringField("Banner title", validators=[InputRequired("Please select a template")])


class BannerEditForm(FlaskForm):
    title = StringField("Banner title", validators=[InputRequired("Enter a banner title")])
    banner = StringField(
        "Banner text",
        validators=[
            InputRequired("Banner text is missing"),
            Length(max=50000, message="Text must be less than 50000 characters"),
        ],
    )
    banner_id = StringField("id")
    delete = BooleanField("Delete banner", default=False)


class Form(FlaskForm):
    def validate(self):
        return "option" in self.data and self.data["option"]


class MyAccountOptionsForm(Form):
    option = RadioField(
        "Label",
        choices=[("value", "change_username"), ("value", "change_name"), ("value", "change_password")],
    )


class ChangePasswordFrom(FlaskForm):
    password = PasswordField("type your password", validators=[DataRequired("Your current password is required")])

    new_password = PasswordField(
        "Create a new password",
        validators=[
            DataRequired("Your new password is required"),
            EqualTo("new_password_confirm", message="Your passwords do not match"),
            Length(
                min=12,
                max=160,
                message="Your password doesn't meet the requirements",
            ),
        ],
    )
    new_password_confirm = PasswordField("Re-type your new password")

    @staticmethod
    def validate_new_password(form, field):
        new_password = field.data
        if (
            new_password.isalnum()
            or not any(char.isupper() for char in new_password)
            or not any(char.isdigit() for char in new_password)
        ):
            raise ValidationError("Your password doesn't meet the requirements")
