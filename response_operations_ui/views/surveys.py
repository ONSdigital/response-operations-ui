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
    return render_template('surveys.html', survey_list=survey_list)


@surveys_bp.route('/<short_name>', methods=['GET'])
@login_required
def view_survey(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    return render_template('survey.html',
                           survey=survey_details['survey'],
                           collection_exercises=survey_details['collection_exercises'])
