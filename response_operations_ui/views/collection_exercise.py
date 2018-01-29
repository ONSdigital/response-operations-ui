import iso8601
import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import convert_events_to_new_format
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.controllers import collection_instrument_controllers, sample_controllers

logger = wrap_logger(logging.getLogger(__name__))

collection_exercise_bp = Blueprint('collection_exercise_bp', __name__,
                                   static_folder='static', template_folder='templates')


@collection_exercise_bp.route('/<short_name>/<period>', methods=['GET'])
@login_required
def view_collection_exercise(short_name, period, error=None, ci_loaded=False, sample_loaded=False):
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
    return render_template('collection-exercise.html',
                           survey=ce_details['survey'],
                           ce=ce_details['collection_exercise'],
                           sample=ce_details['sample_summary'], sample_loaded=sample_loaded,
                           collection_instruments=ce_details['collection_instruments'], ci_loaded=ci_loaded,
                           events=formatted_events,
                           breadcrumbs=breadcrumbs,
                           error=error)


@collection_exercise_bp.route('/<short_name>/<period>', methods=['POST'])
@login_required
def upload(short_name, period):
    if 'load-sample' in request.form:
        return _upload_sample(short_name, period)
    else:
        return _upload_collection_instrument(short_name, period)


def _upload_sample(short_name, period):
    error = _validate_sample()
    sample_loaded = False

    if not error:
        sample_controllers.upload_sample(short_name, period, request.files['sampleFile'])
        sample_loaded = True

    return view_collection_exercise(short_name, period, error=error, sample_loaded=sample_loaded)


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
