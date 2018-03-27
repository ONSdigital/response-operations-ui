import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import map_ce_response_status
from response_operations_ui.controllers import case_controller
from response_operations_ui.controllers import contact_details_controller
from response_operations_ui.controllers import reporting_units_controllers
from response_operations_ui.forms import EditContactDetailsForm
from response_operations_ui.forms import SearchForm

logger = wrap_logger(logging.getLogger(__name__))

reporting_unit_bp = Blueprint('reporting_unit_bp', __name__, static_folder='static', template_folder='templates')


@reporting_unit_bp.route('/<ru_ref>', methods=['GET'])
@login_required
def view_reporting_unit(ru_ref):
    ru_details = reporting_units_controllers.get_reporting_unit(ru_ref)

    ru_details['surveys'] = sorted(ru_details['surveys'], key=lambda survey: survey['surveyRef'])

    respondent = {}
    for survey in ru_details['surveys']:
        survey['collection_exercises'] = sorted(survey['collection_exercises'],
                                                key=lambda ce: ce['scheduledStartDateTime'],
                                                reverse=True)

        for collection_exercise in survey['collection_exercises']:
            collection_exercise['responseStatus'] = map_ce_response_status(collection_exercise['responseStatus'])
            statuses = case_controller.get_available_case_group_statuses(survey['shortName'],
                                                                         collection_exercise['exerciseRef'], ru_ref)
            collection_exercise['statusChangeable'] = len(statuses['available_statuses']) > 0
            collection_exercise['companyRegion'] = map_region(collection_exercise['companyRegion'])

        for respondent in survey['respondents']:
            respondent['status'] = respondent['status'].title()
            respondent['enrolmentStatus'] = respondent['enrolmentStatus'].title()

    survey_arg = request.args.get('survey')
    period_arg = request.args.get('period')
    info_message = None
    if survey_arg and period_arg:
        survey = next(filter(lambda s: s['shortName'] == survey_arg, ru_details['surveys']))
        collection_exercise = next(filter(lambda s: s['exerciseRef'] == period_arg, survey['collection_exercises']))
        new_status = collection_exercise['responseStatus']
        info_message = f'Response status for {survey["surveyRef"]} {survey["shortName"]}' \
                       f' period {period_arg} changed to {new_status}'

    info = request.args.get('info')
    if info:
        info_message = info

    breadcrumbs = [
        {
            "title": "Reporting units",
            "link": "/reporting-units"
        },
        {
            "title": f"{ru_ref}"
        }
    ]
    return render_template('reporting-unit.html', ru_ref=ru_ref, party_id=respondent.get('id'),
                           ru=ru_details['reporting_unit'], surveys=ru_details['surveys'],
                           breadcrumbs=breadcrumbs, info_message=info_message)


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['GET'])
@login_required
def view_contact_details(ru_ref, respondent_id):
    respondent_details = contact_details_controller.get_contact_details(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_details)

    return render_template('edit-contact-details.html', ru_ref=ru_ref, respondent_details=respondent_details,
                           form=form)


@reporting_unit_bp.route('edit-contact-details/<respondent_id>', methods=['POST'])
@login_required
def edit_contact_details(respondent_id):
    ru_ref = request.args.get('ru_ref')
    form = request.form
    contact_details_changed = contact_details_controller.update_contact_details(respondent_id, form)

    ui_message = 'No updates were necessary'
    if 'emailAddress' in contact_details_changed:
        if len(contact_details_changed) > 1:
            ui_message = f'Contact details saved and verification email sent to {form.get("email")}'
        else:
            ui_message = f'Verification email sent to {form.get("email")}'
    elif len(contact_details_changed) > 0:
        ui_message = 'Contact details changed'

    if ru_ref:
        return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, info=ui_message))
    else:
        return redirect(url_for('respondent_bp.respondent_search', respondent_id=respondent_id))


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


@reporting_unit_bp.route('/resend_verification/<ru_ref>/<email>/<party_id>', methods=['GET'])
@login_required
def resend_verification(ru_ref, email, party_id):
    logger.debug("Re-send verification email requested", ru_ref=ru_ref, party_id=party_id)
    return render_template('re-send-verification-email.html', ru_ref=ru_ref, email=email)


@reporting_unit_bp.route('/resend_verification/<ru_ref>/<email>/<party_id>', methods=['POST'])
@login_required
def resent_verification(ru_ref, email, party_id):
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


def map_region(region):
    if region == "YY":
        region = "NI"
    else:
        region = "GB"

    return region
