import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import survey_controllers


logger = wrap_logger(logging.getLogger(__name__))

surveys_bp = Blueprint('surveys_bp', __name__,
                       static_folder='static', template_folder='templates/surveys')


@surveys_bp.route('/', methods=['GET'])
@login_required
def view_surveys():
    survey_list = survey_controllers.get_surveys_list()
    breadcrumbs = [{"title": "Surveys"}]
    return render_template('surveys.html', survey_list=survey_list, breadcrumbs=breadcrumbs)


@surveys_bp.route('/<short_name>', methods=['GET'])
@login_required
def view_survey(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    breadcrumbs = [
        {
            "title": "Surveys",
            "link": "/surveys"
        },
        {
            "title": f"{survey_details['survey']['surveyRef']} {survey_details['survey']['shortName']}",
        }
    ]

    # Mapping backend states to frontend sates for the user
    for collection_exercise_state in survey_details["collection_exercises"]:
        if collection_exercise_state["state"] == "INIT":
            collection_exercise_state["state"] = "Created"

        if collection_exercise_state["state"] == "SCHEDULED":
            collection_exercise_state["state"] = "Scheduled"

        if collection_exercise_state["state"] == "READY_FOR_REVIEW":
            collection_exercise_state["state"] = "Ready for review"

        if collection_exercise_state["state"] == "EXECUTION_STARTED":
            collection_exercise_state["state"] = "Processing"

        if collection_exercise_state["state"] == "READY_FOR_LIVE":
            collection_exercise_state["state"] = "Live"

    return render_template('survey.html',
                           survey=survey_details['survey'],
                           collection_exercises=survey_details['collection_exercises'],
                           survey_state=collection_exercise_state['state'],
                           breadcrumbs=breadcrumbs)
