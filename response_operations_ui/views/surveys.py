import logging
from datetime import datetime
from json import loads, JSONDecodeError

from flask import Blueprint, render_template, request, redirect, session, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import map_collection_exercise_state, convert_events_to_new_format
from response_operations_ui.controllers import survey_controllers, collection_exercise_controllers, \
    collection_instrument_controllers
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.forms import CreateSurveyDetailsForm, LinkCollectionInstrumentForm, EditSurveyDetailsForm

logger = wrap_logger(logging.getLogger(__name__))

surveys_bp = Blueprint('surveys_bp', __name__,
                       static_folder='static', template_folder='templates/surveys')

INFO_MESSAGES = {
    'survey_changed': "Survey details changed",
    'instrument_linked': "Collection exercise linked to survey successfully"
}


@surveys_bp.route('/', methods=['GET'])
@login_required
def view_surveys():
    survey_list = survey_controllers.get_surveys_list()
    breadcrumbs = [{"text": "Surveys"}]
    info_message = INFO_MESSAGES.get(request.args.get('message_key'))
    new_survey = session.pop('new_survey', None)

    return render_template('surveys.html', info_message=info_message,
                           survey_list=survey_list, breadcrumbs=breadcrumbs,
                           new_survey=new_survey)


@surveys_bp.route('/<short_name>', methods=['GET'])
@login_required
def view_survey(short_name):

    survey = survey_controllers.get_survey(short_name)
    breadcrumbs = [
        {
            "text": "Surveys",
            "url": "/surveys"
        },
        {
            "text": f"{survey['surveyRef']} {survey['shortName']}",
        }
    ]

    collection_exercises = collection_exercise_controllers.\
        get_collection_exercises_with_events_and_samples_by_survey_id(survey['id'])

    updated_ce_message = None
    if request.args.get('ce_updated'):
        updated_ce_message = 'Collection exercise details updated'

    created_ce_message = None
    if request.args.get('ce_created'):
        created_ce_message = 'Collection exercise created'

    newly_created_period = request.args.get('new_period')

    # Mapping backend states to frontend sates for the user
    for collex in collection_exercises:
        collex['state'] = map_collection_exercise_state(collex['state'])
        collex['events'] = convert_events_to_new_format(collex['events']) if collex.get('events') else {}

    _sort_collection_exercise(collection_exercises)

    # This is temporary until the survey data includes whether it's an EQ or SEFT.  Until then we'll define the list
    # so we can make the 'link collection instrument' button appear only on EQ surveys.
    eq_surveys = ['MBS', 'QSS', 'QCAS', 'RSI', 'MWSS', 'QBS', 'UKIS', 'QPSESLA', 'QPSESPB', 'QPSESCS',
                  'VACS2', 'VACS3', 'VACS4', 'VACS5', 'Ecommerce', 'CAT', 'COVID']
    is_eq_survey = False
    if short_name in eq_surveys:
        is_eq_survey = True

    return render_template('survey.html',
                           survey=survey,
                           collection_exercises=collection_exercises,
                           breadcrumbs=breadcrumbs, updated_ce_message=updated_ce_message,
                           created_ce_message=created_ce_message, newly_created_period=newly_created_period,
                           is_eq_survey=is_eq_survey)


@surveys_bp.route('/edit-survey-details/<short_name>', methods=['GET'])
@login_required
def view_survey_details(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    form = EditSurveyDetailsForm(form=request.form)

    return render_template('edit-survey-details.html', form=form, short_name=short_name,
                           legal_basis=survey_details['legalBasis'],
                           long_name=survey_details['longName'],
                           survey_ref=survey_details['surveyRef'])


@surveys_bp.route('/edit-survey-details/<short_name>', methods=['POST', 'GET'])
@login_required
def edit_survey_details(short_name):
    form = EditSurveyDetailsForm(form=request.form)
    if not form.validate():
        survey_details = survey_controllers.get_survey(short_name)
        return render_template('edit-survey-details.html', form=form, short_name=short_name, errors=form.errors,
                               legal_basis=survey_details['legalBasis'],
                               long_name=survey_details['longName'],
                               survey_ref=survey_details['surveyRef'],
                               survey_details=survey_details)

    else:
        form = request.form
        survey_controllers.update_survey_details(form.get('hidden_survey_ref'),
                                                 form.get('short_name'),
                                                 form.get('long_name'))
        return redirect(url_for('surveys_bp.view_surveys', message_key='survey_changed'))


@surveys_bp.route('/create', methods=['GET'])
@login_required
def show_create_survey():
    form = CreateSurveyDetailsForm(form=request.form)

    return render_template('create-survey.html', form=form)


@surveys_bp.route('/create', methods=['POST'])
@login_required
def create_survey():
    form = CreateSurveyDetailsForm(form=request.form)
    if not form.validate():
        return render_template('create-survey.html', form=form, errors=form.errors.items())

    try:
        survey_controllers.create_survey(request.form.get('survey_ref'),
                                         request.form.get('short_name'),
                                         request.form.get('long_name'),
                                         request.form.get('legal_basis'))
        session['new_survey'] = {
            'short_name': request.form.get('short_name'),
            'long_name': request.form.get('long_name')
        }
        return redirect(url_for('surveys_bp.view_surveys'))
    except ApiError as err:
        # If it's conflict or bad request assume the service has returned a useful error
        # message as the body of the response
        if err.status_code == 409 or err.status_code == 400:
            return render_template('create-survey.html', form=form, errors=[("", [err.message])])
        else:
            raise


@surveys_bp.route('/<short_name>/link-collection-instrument', methods=['GET'])
@login_required
def get_link_collection_instrument(short_name):
    form = LinkCollectionInstrumentForm(form=request.form)
    short_name_lower = str(short_name).lower()
    survey_id = survey_controllers.get_survey_by_shortname(short_name_lower)['id']
    eq_ci_selectors = collection_instrument_controllers.get_collection_instruments_by_classifier(
        ci_type='EQ',
        survey_id=survey_id)
    logger.info(eq_ci_selectors)
    return render_template('link-collection-instrument.html',
                           short_name=short_name,
                           form=form, eq_ci_selectors=eq_ci_selectors)


@surveys_bp.route('/<short_name>/link-collection-instrument', methods=['POST'])
@login_required
def post_link_collection_instrument(short_name):
    form = LinkCollectionInstrumentForm(form=request.form)
    eq_ci_selectors = []
    try:
        # The eq_id of a collection instrument will ALWAYS be its shortname.
        short_name_lower = str(short_name).lower()
        survey_uuid = survey_controllers.get_survey_by_shortname(short_name_lower)['id']
        eq_ci_selectors = collection_instrument_controllers.get_collection_instruments_by_classifier(
            ci_type='EQ',
            survey_id=survey_uuid)
        if not form.validate():
            return render_template('link-collection-instrument.html',
                                   short_name=short_name,
                                   form=form, errors=form.errors.items(),
                                   eq_ci_selectors=eq_ci_selectors)
        collection_instrument_controllers.link_collection_instrument_to_survey(survey_uuid, short_name_lower,
                                                                               form.formtype.data)
        # Need to get selectors a second time as we just added one and the list from before is outdated.
        eq_ci_selectors = collection_instrument_controllers.get_collection_instruments_by_classifier(
            ci_type='EQ',
            survey_id=survey_uuid)
    except ApiError as err:
        try:
            error_dict = loads(err.message)
            errors = [("formtype", [error_dict['errors'][0]])]
        except (JSONDecodeError, KeyError):
            # If the message isn't JSON, or the 'errors' key doesn't exist, we'll render the message anyway as it
            # might still be helpful.
            errors = [("", [err.message])]

        return render_template('link-collection-instrument.html', form=form, eq_ci_selectors=eq_ci_selectors,
                               errors=errors, short_name=short_name)

    form.formtype.data = ""  # Reset the value on successful submission
    return render_template('link-collection-instrument.html', form=form,
                           eq_ci_selectors=eq_ci_selectors, short_name=short_name)


def _sort_collection_exercise(collection_exercises):
    collection_exercises.sort(key=lambda ce:
                              datetime.strptime(ce['events']['mps']['date'], '%d %b %Y')
                              if 'mps' in ce['events'] else datetime.max)
