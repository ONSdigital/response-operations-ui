import logging

from flask import render_template, request
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.controllers import collection_instrument_controllers

logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
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
    pass


def upload_sample(short_name, period):
    ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)

    upload_file = request.files['sampleFile']

    sample = {"businesses": 1,
              "collection_instruments": 1,
              "submission_time": '13:10 on 11 January 2018'
              }


    # sample = sample_controllers.get_sample_contents(upload_file)
    # sample_controllers.upload_sample(upload_file)

    return render_template('collection-exercise.html',
                           survey=ce_details['survey'], ce=ce_details['collection_exercise'], sample=sample)


def upload_collection_instrument(short_name, period):
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
