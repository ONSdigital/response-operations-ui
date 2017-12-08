import logging

from flask import render_template
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import survey_controllers


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
def view_surveys():

    # survey_list = [
    #     {
    #         "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
    #         "shortName": "BRES",
    #         "longName": "Business Register and Employment Survey",
    #         "surveyRef": "221"
    #     }
    # ]

    survey_list = survey_controllers.get_surveys_list()
    return render_template('surveys.html', survey_list=survey_list)
