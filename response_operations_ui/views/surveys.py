import logging

from flask import render_template, request
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.controllers import collection_instrument_controllers, sample_controllers


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
def view_home():
    return render_template('home.html')


@app.route('/surveys', methods=['GET'])
def view_surveys():
    survey_list = survey_controllers.get_surveys_list()
    return render_template('surveys.html', survey_list=survey_list)


@app.route('/surveys/<short_name>', methods=['GET'])
def view_survey(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    return render_template('survey.html',
                           survey=survey_details['survey'],
                           collection_exercises=survey_details['collection_exercises'])


@app.route('/surveys/<short_name>/<period>', methods=['GET'])
def view_collection_exercise(short_name, period):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    return render_template('collection-exercise.html',
                           survey=ce_details['survey'], ce=ce_details['collection_exercise'])


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

    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)

    if not error:
        sample = sample_controllers.upload_sample(ce_details['collection_exercise']['id'],
                                                  request.files['sampleFile'],
                                                  total_businesses,
                                                  total_ci)

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
    return render_template('collection-exercise.html',
                           survey=ce_details['survey'], ce=ce_details['collection_exercise'], error=error,
                           ci_loaded=ci_loaded)


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
