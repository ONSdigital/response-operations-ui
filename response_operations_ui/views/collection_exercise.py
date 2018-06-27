import iso8601
import json
import logging

from flask import Blueprint, render_template, request, redirect, session, url_for
from flask_login import login_required
from flask import jsonify, make_response
from structlog import wrap_logger

from response_operations_ui.common.filters import get_collection_exercise_by_period
from response_operations_ui.common.mappers import convert_events_to_new_format, map_collection_exercise_state
from response_operations_ui.controllers import collection_instrument_controllers, sample_controllers, \
    collection_exercise_controllers, survey_controllers
from response_operations_ui.forms import EditCollectionExerciseDetailsForm, CreateCollectionExerciseDetailsForm, \
    EventDateForm, RemoveLoadedSample

logger = wrap_logger(logging.getLogger(__name__))

collection_exercise_bp = Blueprint('collection_exercise_bp', __name__,
                                   static_folder='static', template_folder='templates')


def get_success_message(success_key):
    return {
        'sample_removed_success': "Sample removed",
        'sample_loaded_success': "Sample successfully loaded"
    }.get(success_key, None)


def get_error_message(error_key):
    return {
        'sample_removed_error': "Error failed to remove sample"
    }.get(error_key, None)


@collection_exercise_bp.route('/<short_name>/<period>', methods=['GET'])
@login_required
def view_collection_exercise(short_name, period):
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

    success_key = request.args.get('success_key')
    success_message = get_success_message(success_key)

    ce_state = ce_details['collection_exercise']['state']
    show_set_live_button = ce_state in ('READY_FOR_REVIEW', 'FAILEDVALIDATION')
    locked = ce_state in ('LIVE', 'READY_FOR_LIVE', 'EXECUTION_STARTED', 'VALIDATED', 'EXECUTED')
    processing = ce_state in ('EXECUTION_STARTED', 'EXECUTED', 'VALIDATED')
    validation_failed = ce_state == 'FAILEDVALIDATION'
    validation_errors = ce_details['collection_exercise']['validationErrors']
    missing_ci = validation_errors and any('MISSING_COLLECTION_INSTRUMENT' in unit['errors']
                                           for unit in validation_errors)

    ce_details['collection_exercise']['state'] = map_collection_exercise_state(ce_state)  # NOQA
    _format_ci_file_name(ce_details['collection_instruments'], ce_details['survey'])

    events = {'mps', 'go_live', 'return_by', 'exercise_end'}
    event_keys = set(formatted_events.keys())
    if events.difference(event_keys):  # difference will be truthy if any of events are not in _keys
        editable_events = False
    else:
        editable_events = True  # all expected keys are present

    show_msg = request.args.get('show_msg')

    success_panel = request.args.get('success_panel')

    return render_template('collection-exercise.html',
                           breadcrumbs=breadcrumbs,
                           ce=ce_details['collection_exercise'],
                           collection_instruments=ce_details['collection_instruments'],
                           eq_ci_selectors=ce_details['eq_ci_selectors'],
                           error=json.loads(session.get('error')) if session.get('error') else None,
                           events=formatted_events,
                           locked=locked,
                           missing_ci=missing_ci,
                           processing=processing,
                           sample=ce_details['sample_summary'],
                           show_set_live_button=show_set_live_button,
                           survey=ce_details['survey'],
                           success_message=success_message,
                           success_panel=success_panel,
                           validation_failed=validation_failed,
                           show_msg=show_msg,
                           ci_classifiers=ce_details['ci_classifiers']['classifierTypes'],
                           editable_events=editable_events)


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
    success_panel = None
    result = collection_exercise_controllers.execute_collection_exercise(short_name, period)

    if result:
        success_panel = "Collection exercise executed"
    else:
        session['error'] = json.dumps({
            "section": "head",
            "header": "Error: Failed to execute Collection Exercise",
            "message": "Error processing collection exercise"
        })

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name,
                            period=period,
                            success_panel=success_panel))


def _upload_sample(short_name, period):
    error = _validate_sample()

    if not error:
        survey = survey_controllers.get_survey_by_shortname(short_name)
        exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])

        # Find the collection exercise for the given period
        exercise = get_collection_exercise_by_period(exercises, period)

        if not exercise:
            return make_response(jsonify({'message': 'Collection exercise not found'}), 404)
        sample_summary = sample_controllers.upload_sample(short_name, period, request.files['sampleFile'])

        logger.info('Linking sample summary with collection exercise',
                    collection_exercise_id=exercise['id'],
                    sample_id=sample_summary['id'])

        collection_exercise_controllers.link_sample_summary_to_collection_exercise(
            collection_exercise_id=exercise['id'],
            sample_summary_id=sample_summary['id'])

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name,
                            period=period,
                            error=error,
                            show_msg='true'))


def _select_collection_instrument(short_name, period):
    success_panel = None
    cis_selected = request.form.getlist("checkbox-answer")
    cis_added = []

    if cis_selected:
        for ci in cis_selected:
            ci_added = collection_instrument_controllers.link_collection_instrument(request.form['ce_id'], ci)
            cis_added.append(ci_added)

        if all(added for added in cis_added):
            success_panel = "Collection instruments added"
        else:
            session['error'] = json.dumps({
                "section": "ciSelect",
                "header": "Error: Failed to add collection instrument(s)",
                "message": "Please try again"
            })

    else:
        session['error'] = json.dumps({
            "section": "ciSelect",
            "header": "Error: No collection instruments selected",
            "message": "Please select a collection instrument"
        })

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name,
                            period=period,
                            success_panel=success_panel))


def _upload_collection_instrument(short_name, period):
    success_panel = None
    error = _validate_collection_instrument()

    if not error:
        file = request.files['ciFile']
        form_type = _get_form_type(file.filename)
        survey = survey_controllers.get_survey_by_shortname(short_name)
        exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])

        # Find the collection exercise for the given period
        exercise = get_collection_exercise_by_period(exercises, period)
        if not exercise:
            return make_response(jsonify({'message': 'Collection exercise not found'}), 404)

        if collection_instrument_controllers.upload_collection_instrument(exercise['id'], file, form_type):
            success_panel = "Collection instrument loaded"
        else:
            session['error'] = json.dumps({
                "section": "ciFile",
                "header": "Error: Failed to upload collection instrument",
                "message": "Please try again"
            })
    else:
        session['error'] = json.dumps(error)

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name,
                            period=period,
                            success_panel=success_panel))


def _unselect_collection_instrument(short_name, period):
    success_panel = None
    ci_id = request.form.get('ci_id')
    ce_id = request.form.get('ce_id')

    ci_unlinked = collection_instrument_controllers.unlink_collection_instrument(ce_id, ci_id)

    if ci_unlinked:
        success_panel = "Collection instrument removed"
    else:
        session['error'] = json.dumps({"section": "head",
                                       "header": "Error: Failed to remove collection instrument",
                                       "message": "Please try again"})

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name,
                            period=period,
                            success_panel=success_panel))


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
    logger.info("Retrieving collection exercise data for form", short_name=short_name, period=period)
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    form = EditCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    ce_state = ce_details['collection_exercise']['state']
    locked = ce_state in ('LIVE', 'READY_FOR_LIVE', 'EXECUTION_STARTED', 'VALIDATED', 'EXECUTED')

    return render_template('edit-collection-exercise-details.html', survey_ref=ce_details['survey']['surveyRef'],
                           form=form, short_name=short_name, period=period, locked=locked,
                           ce_state=ce_details['collection_exercise']['state'],
                           user_description=ce_details['collection_exercise']['userDescription'],
                           collection_exercise_id=ce_details['collection_exercise']['id'],
                           survey_id=survey_details['survey']['id'])


@collection_exercise_bp.route('/<short_name>/<period>/edit-collection-exercise-details', methods=['POST'])
@login_required
def edit_collection_exercise_details(short_name, period):
    form = EditCollectionExerciseDetailsForm(form=request.form)
    if not form.validate():
        logger.info("Failed validation, retrieving collection exercise data for form",
                    short_name=short_name, period=period)
        ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
        ce_state = ce_details['collection_exercise']['state']
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        locked = ce_state in ('LIVE', 'READY_FOR_LIVE', 'EXECUTION_STARTED', 'VALIDATED', 'EXECUTED')

        return render_template('edit-collection-exercise-details.html', survey_ref=ce_details['survey']['surveyRef'],
                               form=form, short_name=short_name, period=period, locked=locked,
                               ce_state=ce_details['collection_exercise']['state'], errors=form.errors,
                               user_description=ce_details['collection_exercise']['userDescription'],
                               collection_exercise_id=ce_details['collection_exercise']['id'],
                               survey_id=survey_id)

    else:
        logger.info("Updating collection exercise details", short_name=short_name, period=period)
        form = request.form
        collection_exercise_controllers.update_collection_exercise_details(form.get('collection_exercise_id'),
                                                                           form.get('user_description'),
                                                                           form.get('period'))

        return redirect(url_for('surveys_bp.view_survey', short_name=short_name, ce_updated='True'))


@collection_exercise_bp.route('/<survey_ref>-<short_name>/create-collection-exercise', methods=['GET'])
@login_required
def get_create_collection_exercise_form(survey_ref, short_name):
    logger.info("Retrieving survey data for form", short_name=short_name, survey_ref=survey_ref)
    form = CreateCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    return render_template('create-collection-exercise.html', form=form, short_name=short_name,
                           survey_ref=survey_ref, survey_id=survey_details['survey']['id'],
                           survey_name=survey_details['survey']['shortName'])


@collection_exercise_bp.route('/<survey_ref>-<short_name>/create-collection-exercise', methods=['POST'])
@login_required
def create_collection_exercise(survey_ref, short_name):
    logger.info("Attempting to create collection exercise", survey_ref=survey_ref, survey=short_name)
    ce_form = CreateCollectionExerciseDetailsForm(form=request.form)
    form = request.form

    survey_id = form.get('hidden_survey_id')
    survey_name = form.get('hidden_survey_name')

    if not ce_form.validate():
        logger.info("Failed validation, retrieving survey data for form", survey=short_name, survey_ref=survey_ref)
        error = ce_form.errors['period'][1] \
            if ce_form.errors['period'][1] == 'Please enter numbers only for the period' else None
        return render_template('create-collection-exercise.html', form=ce_form, short_name=short_name, errors=error,
                               survey_ref=survey_ref, survey_id=survey_id,
                               survey_name=survey_name)
    else:
        logger.info("Creating collection exercise for survey", survey=short_name, survey_ref=survey_ref)

        created_period = form.get('period')
        ce_details = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)

        for ce in ce_details:
            if ce['exerciseRef'] == str(created_period):
                error = "Please use a period that is not in use by any collection exercise for this survey."
                return render_template('create-collection-exercise.html', form=ce_form, short_name=short_name,
                                       errors=error,
                                       survey_ref=survey_ref, survey_id=survey_id,
                                       survey_name=survey_name)

        collection_exercise_controllers.create_collection_exercise(survey_id,
                                                                   survey_name,
                                                                   form.get('user_description'),
                                                                   form.get('period'))

        logger.info("Successfully created collection exercise", survey=short_name, survey_ref=survey_ref)
        return redirect(url_for('surveys_bp.view_survey', short_name=short_name, ce_created='True',
                                new_period=form.get('period')))


@collection_exercise_bp.route('/<short_name>/<period>/<ce_id>/confirm-create-event/<tag>', methods=['GET'])
@login_required
def get_create_collection_event_form(short_name, period, ce_id, tag):
    logger.info("Retrieving form for create collection exercise event", short_name=short_name, period=period,
                ce_id=ce_id, tag=tag)

    survey = survey_controllers.get_survey(short_name)

    form = EventDateForm()
    event_name = get_event_name(tag)

    logger.info("Successfully retrieved form for create collection exercise event",
                short_name=short_name,
                period=period,
                ce_id=ce_id, tag=tag)

    return render_template('create-ce-event.html',
                           ce_id=ce_id,
                           short_name=short_name,
                           period=period,
                           survey=survey,
                           event_name=event_name,
                           tag=tag,
                           form=form)


@collection_exercise_bp.route('/<short_name>/<period>/<ce_id>/create-event/<tag>', methods=['POST'])
@login_required
def create_collection_exercise_event(short_name, period, ce_id, tag):
    logger.info("Creating collection exercise event",
                short_name=short_name,
                period=period,
                collection_exercise_id=ce_id,
                tag=tag)

    form = EventDateForm(request.form)

    if not form.validate():
        return render_template('create-ce-event.html',
                               ce_id=ce_id,
                               short_name=short_name,
                               period=period,
                               survey=survey_controllers.get_survey(short_name),
                               tag=tag,
                               event_name=get_event_name(tag),
                               form=form)

    day = form.day.data if not len(form.day.data) == 1 else f"0{form.day.data}"
    timestamp_string = f"{form.year.data}{form.month.data}{day}T{form.hour.data}{form.minute.data}"
    timestamp = iso8601.parse_date(timestamp_string)

    collection_exercise_controllers.create_collection_exercise_event(
        collection_exercise_id=ce_id,
        tag=tag,
        timestamp=timestamp)

    success_panel = "Event date added."

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            period=period,
                            short_name=short_name,
                            success_panel=success_panel))


def get_event_name(tag):
    event_names = {
        "mps": "Main print selection",
        "go_live": "Go Live",
        "return_by": "Return by",
        "exercise_end": "Exercise end",
        "reminder": "First reminder",
        "reminder2": "Second reminder",
        "reminder3": "Third reminder",
        "ref_period_start": "Reference period start date",
        "ref_period_end": "Reference period end date"
    }
    return event_names.get(tag)


@collection_exercise_bp.route('/<short_name>/<period>/confirm-remove-sample', methods=['GET'])
@login_required
def get_confirm_remove_sample(short_name, period):
    logger.info("Retrieving confirm remove sample page", short_name=short_name, period=period)
    form = RemoveLoadedSample(form=request.form)
    return render_template('confirm-remove-sample.html', form=form, short_name=short_name, period=period)


@collection_exercise_bp.route('/<short_name>/<period>/confirm-remove-sample', methods=['POST'])
@login_required
def remove_loaded_sample(short_name, period):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    ce_details['sample_summary'] = _format_sample_summary(ce_details['sample_summary'])
    sample_summary_id = ce_details['sample_summary']['id']
    collection_exercise_id = ce_details['collection_exercise']['id']

    unlink_sample_summary = collection_exercise_controllers.unlink_sample_summary(collection_exercise_id,
                                                                                  sample_summary_id)

    if unlink_sample_summary:
        logger.info("Removing sample for collection exercise",
                    short_name=short_name,
                    period=period,
                    collection_exercise_id=collection_exercise_id)
        return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                                short_name=short_name,
                                period=period,
                                success_panel="Sample removed"))
    else:
        logger.info("Failed to remove sample for collection exercise",
                    short_name=short_name,
                    period=period,
                    collection_exercise_id=collection_exercise_id)
        session['error'] = json.dumps({
            "section": "head",
            "header": "Error: Failed to remove sample",
            "message": "Please try again"
        })
        return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                                short_name=short_name,
                                period=period))
