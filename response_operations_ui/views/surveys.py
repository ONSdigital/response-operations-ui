import logging

from flask import render_template
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import survey_controllers


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
