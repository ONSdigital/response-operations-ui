import iso8601
import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import convert_events_to_new_format, map_collection_exercise_state
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.controllers import collection_instrument_controllers, sample_controllers

logger = wrap_logger(logging.getLogger(__name__))

collection_exercise_bp = Blueprint('collection_exercise_bp', __name__,
                                   static_folder='static', template_folder='templates')


@collection_exercise_bp.route('/<short_name>/<period>', methods=['GET'])
@login_required
def view_collection_exercise(short_name, period, error=None, ci_loaded=False, executed=False,
                             sample_loaded=False, ci_added=False):
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
    show_set_live_button = ce_state == 'READY_FOR_REVIEW'
    locked = ce_state in ('LIVE', 'READY_FOR_LIVE', 'EXECUTION_STARTED', 'VALIDATED', 'EXECUTED')
    processing = ce_state in ('EXECUTION_STARTED', 'EXECUTED', 'VALIDATED')

    ce_details['collection_exercise']['state'] = map_collection_exercise_state(ce_state)  # NOQA
    _format_ci_file_name(ce_details['collection_instruments'], ce_details['survey'])

    return render_template('collection-exercise.html',
                           breadcrumbs=breadcrumbs,
                           ce=ce_details['collection_exercise'],
                           ci_added=ci_added,
                           ci_loaded=ci_loaded,
                           collection_instruments=ce_details['collection_instruments'],
                           eq_ci_selectors=ce_details['eq_ci_selectors'],
                           error=error,
                           executed=executed,
                           events=formatted_events,
                           locked=locked,
                           processing=processing,
                           sample=ce_details['sample_summary'],
                           sample_loaded=sample_loaded,
                           show_set_live_button=show_set_live_button,
                           survey=ce_details['survey'])


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
    return view_collection_exercise(short_name, period)


def _set_ready_for_live(short_name, period):
    error = None
    result = collection_exercise_controllers.execute_collection_exercise(short_name, period)
    if not result:
        error = {
            "section": "ce_status",
            "header": "Error: Failed to execute Collection Exercise",
            "message": "Please try again"
        }

    return view_collection_exercise(short_name, period, error=error, executed=result)


def _upload_sample(short_name, period):
    error = _validate_sample()
    sample_loaded = False

    if not error:
        sample_controllers.upload_sample(short_name, period, request.files['sampleFile'])
        sample_loaded = True

    return view_collection_exercise(short_name, period, error=error, sample_loaded=sample_loaded)


def _select_collection_instrument(short_name, period):
    ci_added = False
    error = None
    cis_selected = request.form.getlist("checkbox-answer")

    if cis_selected:
        for ci in cis_selected:
            ci_added = collection_instrument_controllers.link_collection_instrument(request.form['ce_id'], ci)

            if not ci_added:
                error = {
                    "section": "ciSelect",
                    "header": "Error: Failed to add Collection Instrument(s)",
                    "message": "Please try again"
                }
    else:
        error = {
            "section": "ciSelect",
            "header": "Error: No Collection Instruments selected",
            "message": "Please select a collection instrument"
        }

    return view_collection_exercise(short_name, period, error=error, ci_added=ci_added)


def _upload_collection_instrument(short_name, period):
    error = _validate_collection_instrument()
    ci_loaded = False

    if not error:
        ci_loaded = collection_instrument_controllers.upload_collection_instrument(short_name,
                                                                                   period,
                                                                                   request.files['ciFile'])
        if not ci_loaded:
            error = {
                "section": "ciFile",
                "header": "Error: Failed to upload Collection Instrument",
                "message": "Please try again"
            }

    return view_collection_exercise(short_name, period, error=error, ci_loaded=ci_loaded)


def _validate_collection_instrument():
    error = None
    if 'ciFile' in request.files:
        file = request.files['ciFile']
        if not str.endswith(file.filename, '.xlsx'):
            logger.debug('Invalid file format uploaded', filename=file.filename)
            error = {
                "section": "ciFile",
                "header": "Error: wrong file type for Collection instrument",
                "message": "Please use XLSX file only"
            }
    else:
        logger.debug('No file uploaded')
        error = {
            "section": "ciFile",
            "header": "Error: No Collection instrument supplied",
            "message": "Please provide a Collection instrument"
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
