import logging

from flask import render_template, request
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.common.mappers import convert_events_to_new_format
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.controllers import collection_instrument_controllers

logger = wrap_logger(logging.getLogger(__name__))


@app.route('/surveys/<short_name>/<period>', methods=['GET'])
def view_collection_exercise(short_name, period):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    formatted_events = convert_events_to_new_format(ce_details['events'])
    return render_template('collection-exercise.html', survey=ce_details['survey'],
                           ce=ce_details['collection_exercise'],
                           collection_instruments=ce_details['collection_instruments'],
                           events=formatted_events)


@app.route('/surveys/<short_name>/<period>', methods=['POST'])
def upload_collection_instrument(short_name, period):
    error = _validate_collection_instrument()
    ci_loaded = False

    if not error:
        collection_instrument_controllers.upload_collection_instrument(short_name, period, request.files['ciFile'])
        ci_loaded = True

    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    formatted_events = convert_events_to_new_format(ce_details['events'])
    return render_template('collection-exercise.html', survey=ce_details['survey'],
                           ce=ce_details['collection_exercise'], ci_loaded=ci_loaded,
                           collection_instruments=ce_details['collection_instruments'],
                           events=formatted_events)


def _validate_collection_instrument():
    error = None
    if 'ciFile' in request.files:
        file = request.files['ciFile']
        if not str.endswith(file.filename, '.xlsx'):
            logger.debug('Invalid file format uploaded', filename=file.filename)
            error = 'Invalid file format'
    else:
        logger.debug('No file uploaded')
        error = 'File not uploaded'

    return error
