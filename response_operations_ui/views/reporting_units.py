import logging
from datetime import datetime, timezone

from flask import current_app as app
from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required
from flask_paginate import Pagination
from iso8601 import parse_date
from structlog import wrap_logger

from response_operations_ui.common.mappers import map_ce_response_status, map_region
from response_operations_ui.common.respondent_utils import edit_contact
from response_operations_ui.controllers import case_controller, iac_controller, party_controller, \
    reporting_units_controllers
from response_operations_ui.controllers.collection_exercise_controllers import \
    get_case_group_status_by_collection_exercise, get_collection_exercise_by_id
from response_operations_ui.controllers.party_controller import get_respondent_by_party_id
from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.forms import EditContactDetailsForm, RuSearchForm


logger = wrap_logger(logging.getLogger(__name__))

reporting_unit_bp = Blueprint('reporting_unit_bp', __name__, static_folder='static', template_folder='templates')


@reporting_unit_bp.route('/<ru_ref>', methods=['GET'])
@login_required
def view_reporting_unit(ru_ref):
    logger.info("Gathering data to view reporting unit", ru_ref=ru_ref)
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
    surveys_with_latest_case = [
        {
            **survey,
            "case": get_latest_case_with_ce(cases, survey['collection_exercises'])
        }
        for survey in sorted_linked_surveys
    ]

    # Generate appropriate info message is necessary
    # TODO Standardise how the info messages are generated
    survey_arg = request.args.get('survey')
    period_arg = request.args.get('period')
    if survey_arg and period_arg:
        survey = next(filter(lambda s: s['shortName'] == survey_arg, sorted_linked_surveys))
        collection_exercise = next(filter(lambda s: s['exerciseRef'] == period_arg, survey['collection_exercises']))
        new_status = collection_exercise['responseStatus']
        flash(f'Response status for {survey["surveyRef"]} {survey["shortName"]}'
              f' period {period_arg} changed to {new_status}')

    info = request.args.get('info')
    if request.args.get('enrolment_changed'):
        flash('Enrolment status changed', 'information')
    if request.args.get('account_status_changed'):
        flash('Account status changed', 'information')
    elif info:
        flash(info, 'information')

    breadcrumbs = [
        {
            "text": "Reporting units",
            "url": "/reporting-units"
        },
        {
            "text": f"{ru_ref}"
        }
    ]
    logger.info("Successfully gathered data to view reporting unit", ru_ref=ru_ref)
    return render_template('reporting-unit.html', ru_ref=ru_ref, ru=reporting_unit,
                           surveys=surveys_with_latest_case, breadcrumbs=breadcrumbs)


def add_collection_exercise_details(collection_exercise, reporting_unit, case_groups):
    response_status = get_case_group_status_by_collection_exercise(case_groups, collection_exercise['id'])
    reporting_unit_ce = party_controller.get_business_by_party_id(reporting_unit['id'], collection_exercise['id'])
    statuses = case_controller.get_available_case_group_statuses_direct(collection_exercise['id'],
                                                                        reporting_unit['sampleUnitRef'])
    ce_extra = {
        **collection_exercise,
        'responseStatus': map_ce_response_status(response_status),
        'companyName': reporting_unit_ce['name'],
        'companyRegion': map_region(reporting_unit_ce['region']),
        'trading_as': reporting_unit_ce['trading_as'],
        'statuses': statuses.values()
    }
    return ce_extra


def survey_with_respondents_and_exercises(survey, respondents, collection_exercises, ru_ref):
    survey_respondents = [party_controller.add_enrolment_status_to_respondent(respondent, ru_ref, survey['id'])
                          for respondent in respondents
                          if survey['id'] in party_controller.survey_ids_for_respondent(respondent, ru_ref)]
    survey_collection_exercises = [collection_exercise
                                   for collection_exercise in collection_exercises
                                   if survey['id'] == collection_exercise['surveyId']]
    sorted_survey_exercises = sorted(survey_collection_exercises,
                                     key=lambda ce: ce['scheduledStartDateTime'], reverse=True)
    return {
        **survey,
        'respondents': survey_respondents,
        'collection_exercises': sorted_survey_exercises
    }


def get_latest_case_with_ce(cases, collection_exercises):
    # Takes in a list of cases and a list of collection exercises and
    # returns the latest case which is in one of the collection exercises
    ces_ids = [ce['id'] for ce in collection_exercises]
    cases_for_survey = [case
                        for case in cases
                        if case.get('caseGroup', {}).get('collectionExerciseId') in ces_ids]
    cases_for_survey_ordered = sorted(cases_for_survey, key=lambda c: c['createdDateTime'], reverse=True)
    case = next((case for case in cases_for_survey_ordered), None)
    case['activeIAC'] = iac_controller.is_iac_active(case['iac'])
    return case


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['GET'])
@login_required
def view_contact_details(ru_ref, respondent_id):
    respondent_details = party_controller.get_respondent_by_party_id(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_details)

    return render_template('edit-contact-details.html', ru_ref=ru_ref, respondent_details=respondent_details,
                           form=form, tab='reporting_units')


@reporting_unit_bp.route('/<ru_ref>/edit-contact-details/<respondent_id>', methods=['POST'])
@login_required
def edit_contact_details(respondent_id, ru_ref):
    edit_contact(respondent_id)
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref))


@reporting_unit_bp.route('/', methods=['GET'])
@login_required
def search_reporting_unit_home():
    return render_template('reporting-unit-search/reporting-units-search.html',
                           form=RuSearchForm(),
                           breadcrumbs=[{"text": "Reporting units"}])


@reporting_unit_bp.route('/', methods=['POST'])
@login_required
def search_redirect():
    form = RuSearchForm(request.form)

    if form.validate_on_submit():
        query = request.form.get('query')

        return redirect(url_for('reporting_unit_bp.search_reporting_units', query=query))


@reporting_unit_bp.route('/search', methods=['GET'])
@login_required
def search_reporting_units():
    search_key_words = request.values.get('query', '')
    page = request.values.get('page', '1')
    limit = app.config["PARTY_BUSINESS_RESULTS_PER_PAGE"]
    breadcrumbs = [{"text": "Reporting units"}]
    form = RuSearchForm()
    form.query.data = search_key_words

    response_data = reporting_units_controllers.search_reporting_units(search_key_words, limit, page)
    business_list = response_data['businesses']
    total_business_count = response_data['total_business_count']

    offset = (int(page) - 1) * limit
    last_index = (limit + offset) if total_business_count >= limit else total_business_count

    pagination = Pagination(page=int(page),
                            per_page=limit,
                            total=total_business_count,
                            record_name='Business',
                            prev_label='Previous',
                            next_label='Next',
                            outer_window=0,
                            format_total=True,
                            format_number=True,
                            show_single_page=False)

    return render_template('reporting-unit-search/reporting-units.html',
                           form=form,
                           business_list=business_list,
                           total_business_count=total_business_count,
                           breadcrumbs=breadcrumbs,
                           first_index=1 + offset,
                           last_index=last_index,
                           pagination=pagination,
                           show_pagination=bool(total_business_count > limit))


@reporting_unit_bp.route('/resend_verification/<ru_ref>/<party_id>', methods=['GET'])
@login_required
def view_resend_verification(ru_ref, party_id):
    logger.info("Re-send verification email requested", ru_ref=ru_ref, party_id=party_id)
    respondent = party_controller.get_respondent_by_party_id(party_id)
    email = respondent['pendingEmailAddress'] if 'pendingEmailAddress' in respondent \
        else respondent['emailAddress']

    return render_template('re-send-verification-email.html', ru_ref=ru_ref, email=email, tab='reporting_units')


@reporting_unit_bp.route('/resend_verification/<ru_ref>/<party_id>', methods=['POST'])
@login_required
def resend_verification(ru_ref, party_id):
    reporting_units_controllers.resend_verification_email(party_id)
    logger.info("Re-sent verification email.", party_id=party_id)
    flash('Verification email re-sent')
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref))


@reporting_unit_bp.route('/<ru_ref>/new_enrolment_code', methods=['GET'])
@login_required
def generate_new_enrolment_code(ru_ref):
    case_id = request.args.get('case_id')
    reporting_units_controllers.generate_new_enrolment_code(case_id)
    case = case_controller.get_case_by_id(case_id)
    return render_template('new-enrolment-code.html',
                           iac=case['iac'],
                           ru_ref=ru_ref,
                           ru_name=request.args.get('ru_name'),
                           trading_as=request.args.get('trading_as'),
                           survey_name=request.args.get('survey_name'),
                           survey_ref=request.args.get('survey_ref'))


@reporting_unit_bp.route('/<ru_ref>/change-enrolment-status', methods=['GET'])
@login_required
def confirm_change_enrolment_status(ru_ref):
    return render_template('confirm-enrolment-change.html', business_id=request.args['business_id'], ru_ref=ru_ref,
                           ru_name=request.args.get('ru_name'),
                           trading_as=request.args['trading_as'], survey_id=request.args['survey_id'],
                           survey_name=request.args['survey_name'], respondent_id=request.args['respondent_id'],
                           first_name=request.args['respondent_first_name'],
                           last_name=request.args['respondent_last_name'],
                           change_flag=request.args['change_flag'],
                           tab=request.args['tab'])


@reporting_unit_bp.route('/<ru_ref>/change-respondent-status', methods=['GET'])
@login_required
def confirm_change_respondent_status(ru_ref):
    respondent = get_respondent_by_party_id(request.args['party_id'])
    return render_template('confirm-respondent-status-change.html',
                           ru_ref=ru_ref,
                           respondent_id=respondent['id'],
                           first_name=respondent['firstName'],
                           last_name=respondent['lastName'],
                           email_address=respondent['emailAddress'],
                           change_flag=request.args['change_flag'],
                           tab=request.args['tab'])


@reporting_unit_bp.route('/<ru_ref>/change-enrolment-status', methods=['POST'])
@login_required
def change_enrolment_status(ru_ref):
    reporting_units_controllers.change_enrolment_status(business_id=request.args['business_id'],
                                                        respondent_id=request.args['respondent_id'],
                                                        survey_id=request.args['survey_id'],
                                                        change_flag=request.args['change_flag'])
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, enrolment_changed='True'))


@reporting_unit_bp.route('/<ru_ref>/change-respondent-status', methods=['POST'])
@login_required
def change_respondent_status(ru_ref):
    reporting_units_controllers.change_respondent_status(respondent_id=request.args['respondent_id'],
                                                         change_flag=request.args['change_flag'])
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, account_status_changed='True'))
