import logging

from flask import render_template
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import survey_controllers


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
def view_surveys():
    # survey_list = survey_controllers.get_surveys_list()
    survey_list = [
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            "shortName": "RSI",
            "longName": "Monthly Business Survey - Retail Sales Index",
            "surveyRef": "023",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "BRUS",
            "longName": "Business Register and Umployment Survey",
            "surveyRef": "222",
            "legal_basis": "Statistics of Trade Act 1947"
        }
    ]
    return render_template('surveys.html', survey_list=survey_list)


@app.route('/surveys/<short_name>', methods=['GET'])
def view_survey(short_name):
    survey = survey_controllers.get_survey(short_name)
    return render_template('survey.html', survey=survey)
