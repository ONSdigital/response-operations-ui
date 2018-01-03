import logging

from flask import render_template
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers


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
    return render_template('collection-exercise.html', ce=ce_details, period=period)
