import datetime
import logging

from flask import render_template, request
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.controllers import collection_instrument_controllers, sample_controllers

logger = wrap_logger(logging.getLogger(__name__))


@app.route('/surveys/<short_name>/<period>', methods=['GET'])
def view_collection_exercise(short_name, period):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    return render_template('collection-exercise.html', survey=ce_details['survey'],
                           ce=ce_details['collection_exercise'],
                           collection_instruments=ce_details['collection_instruments'])


@app.route('/surveys/<short_name>/<period>', methods=['POST'])
def upload(short_name, period):
    if 'load-sample' in request.form:
        return _upload_sample(short_name, period)
    else:
        return _upload_collection_instrument(short_name, period)


def _upload_sample(short_name, period):
    error = _validate_sample()
    sample = False
    total_businesses = request.form.get('sample-businesses')
    total_ci = request.form.get('sample-collection-instruments')

    if not error:
        upload_receipt = sample_controllers.upload_sample(short_name, period, request.files['sampleFile'])
        sample = _sample_summary(total_businesses, total_ci, upload_receipt.get('ingestDateTime'))

    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)

    return render_template('collection-exercise.html',
                           survey=ce_details['survey'], ce=ce_details['collection_exercise'], sample=sample,
                           error=error)


def _upload_collection_instrument(short_name, period):
    error = _validate_collection_instrument()
    ci_loaded = False

    if not error:
        collection_instrument_controllers.upload_collection_instrument(short_name, period, request.files['ciFile'])
        ci_loaded = True

    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    return render_template('collection-exercise.html', survey=ce_details['survey'],
                           ce=ce_details['collection_exercise'], ci_loaded=ci_loaded,
                           collection_instruments=ce_details['collection_instruments'])


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


def _sample_summary(total_businesses, total_ci, submission_time_stamp):
    sample = {"businesses": total_businesses,
              "collection_instruments": total_ci
              }

    if submission_time_stamp:
        submission_datetime = datetime.datetime.strptime(submission_time_stamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        submission_time = submission_datetime.strftime("%I:%M%p on %B %d, %Y")
        sample["submission_time"] = submission_time

    return sample

