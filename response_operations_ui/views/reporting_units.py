import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import map_ce_response_status
from response_operations_ui.controllers import case_controller
from response_operations_ui.controllers import edit_contact_details_controller
from response_operations_ui.controllers import reporting_units_controllers
from response_operations_ui.forms import EditContactDetailsForm
from response_operations_ui.forms import SearchForm

logger = wrap_logger(logging.getLogger(__name__))

reporting_unit_bp = Blueprint('reporting_unit_bp', __name__, static_folder='static', template_folder='templates')


@reporting_unit_bp.route('/<ru_ref>', methods=['GET'])
@login_required
def view_reporting_unit(ru_ref):
    edit_details = request.args.get('edit_details')
    ru_details = reporting_units_controllers.get_reporting_unit(ru_ref)

    ru_details['surveys'] = sorted(ru_details['surveys'], key=lambda survey: survey['surveyRef'])

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

    breadcrumbs = [
        {
            "title": "Reporting units",
            "link": "/reporting-units"
        },
        {
            "title": f"{ru_ref}"
        }
    ]

    survey_arg = request.args.get('survey')
    period_arg = request.args.get('period')
    info_message = None
    if survey_arg and period_arg:
        survey = next(filter(lambda s: s['shortName'] == survey_arg, ru_details['surveys']))
        collection_exercise = next(filter(lambda s: s['exerciseRef'] == period_arg, survey['collection_exercises']))
        new_status = collection_exercise['responseStatus']
        info_message = f'Response status for {survey["surveyRef"]} {survey["shortName"]}' \
                       f' period {period_arg} changed to {new_status}'

    return render_template('reporting-unit.html', ru=ru_details['reporting_unit'], surveys=ru_details['surveys'],
                           breadcrumbs=breadcrumbs, info_message=info_message, edit_details=edit_details)


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['GET'])
@login_required
def view_contact_details(ru_ref, respondent_id):
    respondent_details = edit_contact_details_controller.get_contact_details(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_details)

    return render_template('edit-contact-details.html', ru_ref=ru_ref, respondent_details=respondent_details,
                           form=form)


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['POST'])
@login_required
def edit_contact_details(ru_ref, respondent_id):
    form = EditContactDetailsForm(request.form)

    edit_details_data = build_contact_details(request.form, respondent_id)

    edit_successfully = edit_contact_details_controller.edit_contact_details(edit_details_data, respondent_id)

    if not edit_successfully:
        respondent_details = edit_contact_details_controller.get_contact_details(respondent_id)
        logger.info('Error submitting respondent details', respondent_id=respondent_id)
        return render_template('edit-contact-details.html', ru_ref=ru_ref, form=form, error=True,
                               respondent_details=respondent_details)

    name_or_num_changed = has_name_or_number_changed(edit_details_data)  # TODO: Do we need this for name or num?
    email_changed = has_email_changed(edit_details_data)

    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, edit_details=True,
                            name_or_num_changed=name_or_num_changed, email_changed=email_changed,
                            email=edit_details_data['email_address']))


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


def has_email_changed(edit_details_data):
    return edit_details_data['email_address'] != edit_details_data['new_email_address']

# TODO: Is this needed?
def has_name_or_number_changed(edit_details_data):
    return True


def build_contact_details(form, respondent_id):
    return {
        "respondent_id": respondent_id,
        "first_name": form.get('hidden_first_name'),
        "last_name": form.get('hidden_last_name'),
        "email_address": form.get('hidden_email'),
        "telephone": form.get('hidden_telephone'),
        "new_first_name": form.get('first_name'),
        "new_last_name": form.get('last_name'),
        "new_email_address": form.get('email'),
        "new_telephone": form.get('telephone')
    }
