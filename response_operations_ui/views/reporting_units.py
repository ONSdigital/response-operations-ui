from datetime import datetime, timezone
import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from iso8601 import parse_date
from structlog import wrap_logger

from response_operations_ui.controllers.collection_exercise_controllers import add_collection_exercise_details, \
    get_collection_exercise_by_id
from response_operations_ui.controllers.survey_controllers import get_survey_by_id, \
    survey_with_respondents_and_exercises
from response_operations_ui.controllers import case_controller, iac_controller, party_controller, \
    reporting_units_controllers
from response_operations_ui.forms import EditContactDetailsForm, SearchForm

logger = wrap_logger(logging.getLogger(__name__))

reporting_unit_bp = Blueprint('reporting_unit_bp', __name__, static_folder='static', template_folder='templates')


@reporting_unit_bp.route('/<ru_ref>', methods=['GET'])
@login_required
def view_reporting_unit(ru_ref):
    # Make some initial calls to retrieve some data we'll need
    reporting_unit = party_controller.get_party_by_ru_ref(ru_ref)
    cases = case_controller.get_cases_by_business_party_id(reporting_unit['id'])
    case_groups = case_controller.get_case_groups_by_business_party_id(reporting_unit['id'])

    # Get all collection exercises for retrieved case groups
    collection_exercise_ids = {case_group['collectionExerciseId'] for case_group in case_groups}
    collection_exercises = [get_collection_exercise_by_id(ce_id) for ce_id in collection_exercise_ids]

    # Add extra collection exercise details and filter by live date
    now = datetime.now(timezone.utc)
    live_collection_exercises = [add_collection_exercise_details(ce, reporting_unit, case_groups)
                                 for ce in collection_exercises
                                 if parse_date(ce['scheduledStartDateTime']) < now]

    # Get all related surveys for gathered collection exercises
    survey_ids = {collection_exercise['surveyId'] for collection_exercise in live_collection_exercises}
    surveys = [get_survey_by_id(survey_id) for survey_id in survey_ids]

    # Get all respondents for the given ru
    respondents = [party_controller.get_respondent_by_party_id(respondent['partyId'])
                   for respondent in reporting_unit.get('associations')]

    # Link collection exercises and respondents to appropriate surveys
    linked_surveys = [survey_with_respondents_and_exercises(survey, respondents, live_collection_exercises, ru_ref)
                      for survey in surveys]
    sorted_linked_surveys = sorted(linked_surveys, key=lambda survey: survey['surveyRef'])

    # Add latest active iac code to surveys
    surveys_with_iacs = [
        {
            **survey,
            "activeIacCode": iac_controller.get_latest_active_iac_code(cases, survey['collection_exercises'])
        }
        for survey in sorted_linked_surveys
    ]

    # Generate appropriate info message is necessary
    # TODO Standardise how the info messages are generated
    survey_arg = request.args.get('survey')
    period_arg = request.args.get('period')
    info_message = None
    if survey_arg and period_arg:
        survey = next(filter(lambda s: s['shortName'] == survey_arg, sorted_linked_surveys))
        collection_exercise = next(filter(lambda s: s['exerciseRef'] == period_arg, survey['collection_exercises']))
        new_status = collection_exercise['responseStatus']
        info_message = f'Response status for {survey["surveyRef"]} {survey["shortName"]}' \
                       f' period {period_arg} changed to {new_status}'

    info = request.args.get('info')
    if info:
        info_message = info
    if request.args.get('enrolment_changed'):
        info_message = 'Enrolment status changed'

    breadcrumbs = [
        {
            "title": "Reporting units",
            "link": "/reporting-units"
        },
        {
            "title": f"{ru_ref}"
        }
    ]
    return render_template('reporting-unit.html', ru_ref=ru_ref, ru=reporting_unit,
                           surveys=surveys_with_iacs, breadcrumbs=breadcrumbs,
                           info_message=info_message, enrolment_changed=request.args.get('enrolment_changed'))


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['GET'])
@login_required
def view_contact_details(ru_ref, respondent_id):
    respondent_details = party_controller.get_respondent_by_party_id(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_details)

    return render_template('edit-contact-details.html', ru_ref=ru_ref, respondent_details=respondent_details,
                           form=form)


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['POST'])
@login_required
def edit_contact_details(ru_ref, respondent_id):
    form = request.form
    contact_details_changed = party_controller.update_contact_details(ru_ref, respondent_id, form)

    ui_message = 'No updates were necessary'
    if 'emailAddress' in contact_details_changed:
        ui_message = f'Contact details changed and verification email sent to {form.get("email")}'
    elif len(contact_details_changed) > 0:
        ui_message = 'Contact details changed'

    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, info=ui_message))


@reporting_unit_bp.route('/', methods=['GET', 'POST'])
@login_required
def search_reporting_units():
    form = SearchForm(request.form)
    breadcrumbs = [{"title": "Reporting units"}]
    business_list = None

    if form.validate_on_submit():
        query = request.form.get('query')

        business_list = reporting_units_controllers.search_reporting_units(query)

    return render_template('reporting-units.html', business_list=business_list, form=form, breadcrumbs=breadcrumbs)


@reporting_unit_bp.route('/resend_verification/<ru_ref>/<party_id>', methods=['GET'])
@login_required
def view_resend_verification(ru_ref, party_id):
    logger.debug("Re-send verification email requested", ru_ref=ru_ref, party_id=party_id)
    respondent = party_controller.get_respondent_by_party_id(party_id)
    return render_template('re-send-verification-email.html', ru_ref=ru_ref, email=respondent['emailAddress'])


@reporting_unit_bp.route('/resend_verification/<ru_ref>/<party_id>', methods=['POST'])
@login_required
def resend_verification(ru_ref, party_id):
    reporting_units_controllers.resend_verification_email(party_id)
    logger.info("Re-sent verification email.", party_id=party_id)
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref,
                            info='Verification email re-sent'))


@reporting_unit_bp.route('/<ru_ref>/<collection_exercise_id>/new_enrolment_code', methods=['GET'])
@login_required
def generate_new_enrolment_code(ru_ref, collection_exercise_id):
    case = reporting_units_controllers.generate_new_enrolment_code(collection_exercise_id, ru_ref)
    return render_template('new-enrolment-code.html', case=case, ru_ref=ru_ref,
                           trading_as=request.args.get('trading_as'),
                           survey_name=request.args.get('survey_name'),
                           survey_ref=request.args.get('survey_ref'))


@reporting_unit_bp.route('/<ru_ref>/change-enrolment-status', methods=['GET'])
@login_required
def confirm_change_enrolment_status(ru_ref):
    return render_template('confirm-enrolment-change.html', business_id=request.args['business_id'], ru_ref=ru_ref,
                           trading_as=request.args['trading_as'], survey_id=request.args['survey_id'],
                           survey_name=request.args['survey_name'], respondent_id=request.args['respondent_id'],
                           first_name=request.args['respondent_first_name'],
                           last_name=request.args['respondent_last_name'],
                           change_flag=request.args['change_flag'])


@reporting_unit_bp.route('/<ru_ref>/change-enrolment-status', methods=['POST'])
@login_required
def change_enrolment_status(ru_ref):
    reporting_units_controllers.change_enrolment_status(business_id=request.args['business_id'],
                                                        respondent_id=request.args['respondent_id'],
                                                        survey_id=request.args['survey_id'],
                                                        change_flag=request.args['change_flag'])
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, enrolment_changed='True'))
