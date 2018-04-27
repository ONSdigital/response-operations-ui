import iso8601
import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import convert_events_to_new_format, map_collection_exercise_state
from response_operations_ui.controllers import collection_instrument_controllers, sample_controllers, \
    collection_exercise_controllers, survey_controllers
from response_operations_ui.forms import EditCollectionExerciseDetailsForm, CreateCollectionExerciseDetailsForm

logger = wrap_logger(logging.getLogger(__name__))

collection_exercise_bp = Blueprint('collection_exercise_bp', __name__,
                                   static_folder='static', template_folder='templates')


@collection_exercise_bp.route('/<short_name>/<period>', methods=['GET'])
@login_required
def view_collection_exercise(short_name, period, error=None, success_panel=None):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    ce_details['sample_summary'] = _format_sample_summary(ce_details['sample_summary'])
    formatted_events = convert_events_to_new_format(ce_details['events'])

    breadcrumbs = [
        {
            "title": "Surveys",
            "link": "/surveys"
        },
        {
            "title": f"{ce_details['survey']['surveyRef']} {ce_details['survey']['shortName']}",
            "link": f"/surveys/{ce_details['survey']['shortName'].replace(' ', '')}"
        },
        {
            "title": f"{ce_details['collection_exercise']['exerciseRef']}"
        }
    ]

    ce_state = ce_details['collection_exercise']['state']
    show_set_live_button = ce_state in ('READY_FOR_REVIEW', 'FAILEDVALIDATION')
    locked = ce_state in ('LIVE', 'READY_FOR_LIVE', 'EXECUTION_STARTED', 'VALIDATED', 'EXECUTED')
    processing = ce_state in ('EXECUTION_STARTED', 'EXECUTED', 'VALIDATED')
    validation_failed = ce_state == 'FAILEDVALIDATION'
    show_edit_period = ce_state not in ('READY_FOR_LIVE', 'LIVE')
    validation_errors = ce_details['collection_exercise']['validationErrors']
    missing_ci = validation_errors and any('MISSING_COLLECTION_INSTRUMENT' in unit['errors']
                                           for unit in validation_errors)

    ce_details['collection_exercise']['state'] = map_collection_exercise_state(ce_state)  # NOQA
    _format_ci_file_name(ce_details['collection_instruments'], ce_details['survey'])

    return render_template('collection-exercise.html',
                           breadcrumbs=breadcrumbs,
                           ce=ce_details['collection_exercise'],
                           success_panel=success_panel,
                           collection_instruments=ce_details['collection_instruments'],
                           eq_ci_selectors=ce_details['eq_ci_selectors'],
                           error=error,
                           events=formatted_events,
                           locked=locked,
                           missing_ci=missing_ci,
                           processing=processing,
                           sample=ce_details['sample_summary'],
                           show_set_live_button=show_set_live_button,
                           survey=ce_details['survey'],
                           validation_failed=validation_failed,
                           show_edit_period=show_edit_period,
                           ci_classifiers=ce_details['ci_classifiers']['classifierTypes'])


@collection_exercise_bp.route('/<short_name>/<period>', methods=['POST'])
@login_required
def post_collection_exercise(short_name, period):
    if 'load-sample' in request.form:
        return _upload_sample(short_name, period)
    elif 'load-ci' in request.form:
        return _upload_collection_instrument(short_name, period)
    elif 'ready-for-live' in request.form:
        return _set_ready_for_live(short_name, period)
    elif 'select-ci' in request.form:
        return _select_collection_instrument(short_name, period)
    elif 'unselect-ci' in request.form:
        return _unselect_collection_instrument(short_name, period)
    return view_collection_exercise(short_name, period)


@collection_exercise_bp.route('response_chasing/<ce_id>/<survey_id>', methods=['GET'])
@login_required
def response_chasing(ce_id, survey_id):
    logger.debug('Response chasing', ce_id=ce_id, survey_id=survey_id)
    response = collection_exercise_controllers.download_report(ce_id, survey_id)
    return response.content, response.status_code, response.headers.items()


def _set_ready_for_live(short_name, period):
    error = None
    success_panel = None
    result = collection_exercise_controllers.execute_collection_exercise(short_name, period)

    if result:
        success_panel = {
            "id": "execution-success",
            "message": "Collection exercise executed"
        }
    else:
        error = {
            "section": "ce_status",
            "header": "Error: Failed to execute Collection Exercise",
            "message": "Please try again"
        }

    return view_collection_exercise(short_name, period, error=error, success_panel=success_panel)


def _upload_sample(short_name, period):
    success_panel = None
    error = _validate_sample()

    if not error:
        sample_controllers.upload_sample(short_name, period, request.files['sampleFile'])
        success_panel = {
            "id": "sample-success",
            "message": "Sample successfully loaded"
        }

    return view_collection_exercise(short_name, period, error=error, success_panel=success_panel)


def _select_collection_instrument(short_name, period):
    success_panel = None
    error = None
    cis_selected = request.form.getlist("checkbox-answer")
    cis_added = []

    if cis_selected:
        for ci in cis_selected:
            ci_added = collection_instrument_controllers.link_collection_instrument(request.form['ce_id'], ci)
            cis_added.append(ci_added)

        if all(added for added in cis_added):
            success_panel = {
                "id": "collection-instrument-added-success",
                "message": "Collection instruments added"
            }
        else:
            error = {
                "section": "ciSelect",
                "header": "Error: Failed to add collection instrument(s)",
                "message": "Please try again"
            }

    else:
        error = {
            "section": "ciSelect",
            "header": "Error: No collection instruments selected",
            "message": "Please select a collection instrument"
        }

    return view_collection_exercise(short_name, period, error=error, success_panel=success_panel)


def _upload_collection_instrument(short_name, period):
    success_panel = None
    error = _validate_collection_instrument()

    if not error:
        file = request.files['ciFile']
        form_type = _get_form_type(file.filename)
        ci_loaded = collection_instrument_controllers.upload_collection_instrument(short_name, period, file, form_type)
        if ci_loaded:
            success_panel = {
                "id": "collection-instrument-success",
                "message": "Collection instrument loaded"
            }
        else:
            error = {
                "section": "ciFile",
                "header": "Error: Failed to upload collection instrument",
                "message": "Please try again"
            }

    return view_collection_exercise(short_name, period, error=error, success_panel=success_panel)


def _unselect_collection_instrument(short_name, period):
    error = None
    success_panel = None
    ci_id = request.form.get('ci_id')
    ce_id = request.form.get('ce_id')

    ci_unlinked = collection_instrument_controllers.unlink_collection_instrument(ce_id, ci_id)

    if ci_unlinked:
        success_panel = {
            "id": "collection-instrument-removed-success",
            "message": "Collection instrument removed"

        }
    else:
        error = {
            "header": "Error: Failed to remove collection instrument"
        }

    return view_collection_exercise(short_name, period, error=error, success_panel=success_panel)


def _validate_collection_instrument():
    error = None
    if 'ciFile' in request.files:
        file = request.files['ciFile']
        if not str.endswith(file.filename, '.xlsx'):
            logger.debug('Invalid file format uploaded', filename=file.filename)
            error = {
                "section": "ciFile",
                "header": "Error: wrong file type for collection instrument",
                "message": "Please use XLSX file only"
            }
        else:
            # file name format is surveyId_period_formType
            form_type = _get_form_type(file.filename) if file.filename.count('_') == 2 else ''
            if not form_type.isdigit() or len(form_type) != 4:
                logger.debug('Invalid file format uploaded', filename=file.filename)
                error = {
                    "section": "ciFile",
                    "header": "Error: invalid file name format for collection instrument",
                    "message": "Please provide file with correct form type in file name"
                }
    else:
        logger.debug('No file uploaded')
        error = {
            "section": "ciFile",
            "header": "Error: No collection instrument supplied",
            "message": "Please provide a collection instrument"
        }
    return error


def _validate_sample():
    error = None
    if 'sampleFile' in request.files:
        file = request.files['sampleFile']
        if not str.endswith(file.filename, '.csv'):
            logger.debug('Invalid file format uploaded', filename=file.filename)
            error = 'Invalid file format'
    else:
        logger.debug('No file uploaded')
        error = 'File not uploaded'

    return error


def _format_sample_summary(sample):

    if sample and sample.get('ingestDateTime'):
        submission_datetime = iso8601.parse_date(sample['ingestDateTime'])
        submission_time = submission_datetime.strftime("%I:%M%p on %B %d, %Y")
        sample["ingestDateTime"] = submission_time

    return sample


def _format_ci_file_name(collection_instruments, survey_details):
    for ci in collection_instruments:
        if 'xlsx' not in ci.get('file_name', ''):
            ci['file_name'] = f"{survey_details['surveyRef']} {ci['file_name']} eQ"


def _get_form_type(file_name):
    file_name = file_name.split(".")[0]
    return file_name.split("_")[2]  # file name format is surveyId_period_formType


@collection_exercise_bp.route('/<short_name>/<period>/edit-collection-exercise-details', methods=['GET'])
@login_required
def view_collection_exercise_details(short_name, period):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    form = EditCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    ce_state = ce_details['collection_exercise']['state']
    show_edit_period = ce_state not in ('READY_FOR_LIVE', 'LIVE')

    return render_template('edit-collection-exercise-details.html', survey_ref=ce_details['survey']['surveyRef'],
                           form=form, short_name=short_name, period=period, show_edit_period=show_edit_period,
                           ce_state=ce_details['collection_exercise']['state'],
                           user_description=ce_details['collection_exercise']['userDescription'],
                           collection_exercise_id=ce_details['collection_exercise']['id'],
                           survey_id=survey_details['survey']['id'])


@collection_exercise_bp.route('/<short_name>/<period>/edit-collection-exercise-details', methods=['POST'])
@login_required
def edit_collection_exercise_details(short_name, period):
    form = EditCollectionExerciseDetailsForm(form=request.form)
    if not form.validate():
        ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
        ce_state = ce_details['collection_exercise']['state']
        survey_details = survey_controllers.get_survey(short_name)
        show_edit_period = ce_state not in ('READY_FOR_LIVE', 'LIVE')

        return render_template('edit-collection-exercise-details.html', survey_ref=ce_details['survey']['surveyRef'],
                               form=form, short_name=short_name, period=period, show_edit_period=show_edit_period,
                               ce_state=ce_details['collection_exercise']['state'], errors=form.errors,
                               user_description=ce_details['collection_exercise']['userDescription'],
                               collection_exercise_id=ce_details['collection_exercise']['id'],
                               survey_id=survey_details['survey']['id'])

    else:
        form = request.form
        collection_exercise_controllers.update_collection_exercise_details(form.get('collection_exercise_id'),
                                                                           form.get('user_description'),
                                                                           form.get('period'))

        return redirect(url_for('surveys_bp.view_survey', short_name=short_name, ce_updated='True'))


@collection_exercise_bp.route('/<survey_ref>-<short_name>/create-collection-exercise', methods=['GET'])
@login_required
def get_create_collection_exercise_form(survey_ref, short_name):
    form = CreateCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    return render_template('create-collection-exercise.html', form=form, short_name=short_name,
                           survey_ref=survey_ref, survey_id=survey_details['survey']['id'],
                           survey_name=survey_details['collection_exercises'][0]['name'])


@collection_exercise_bp.route('/<survey_ref>-<short_name>/create-collection-exercise', methods=['POST'])
@login_required
def create_collection_exercise(survey_ref, short_name):
    form = CreateCollectionExerciseDetailsForm(form=request.form)
    if not form.validate():
        survey_details = survey_controllers.get_survey(short_name)
        return render_template('create-collection-exercise.html', form=form, short_name=short_name, errors=form.errors,
                               survey_ref=survey_ref, survey_id=survey_details['survey']['id'],
                               survey_name=survey_details['collection_exercises'][0]['name'])

    else:
        form = request.form
        collection_exercise_controllers.create_collection_exercise(form.get('hidden_survey_id'),
                                                                   form.get('hidden_survey_name'),
                                                                   form.get('user_description'),
                                                                   form.get('period'))

        return redirect(url_for('surveys_bp.view_survey', short_name=short_name, ce_created='True',
                                new_period=form.get('period')))
