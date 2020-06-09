
import logging

from flask import Blueprint, render_template, redirect, request, session, url_for
from flask import current_app as app
from flask_login import login_required
from requests.exceptions import ConnectionError, HTTPError
from structlog import wrap_logger

from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.common.filters import get_current_collection_exercise
from response_operations_ui.common.mappers import convert_event_list_to_dictionary
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))

home_bp = Blueprint('home_bp', __name__, static_folder='static', template_folder='templates')


@home_bp.route('/', methods=['GET'])
@login_required
def home():
    overview_survey = session.get('overview_survey')
    if not session.get('overview_survey'):
        return redirect(url_for('home_bp.get_overview_survey'))

    survey = survey_controllers.get_survey_by_shortname(overview_survey)
    collection_exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
    current_collection_exercise = get_current_collection_exercise(collection_exercises)
    if not current_collection_exercise:
        return render_template('overview/no_collection_exercise_overview.html', survey=overview_survey)

    formatted_data = format_data_for_template(current_collection_exercise, survey)
    return render_template('overview/overview.html', data=formatted_data)


@home_bp.route('/choose-overview-survey', methods=['GET'])
@login_required
def get_overview_survey():
    survey_list = survey_controllers.get_surveys_list()
    breadcrumbs = [{"text": "Overview"}]
    return render_template('choose-overview-survey.html', survey_list=survey_list, breadcrumbs=breadcrumbs)


@home_bp.route('/choose-overview-survey', methods=['POST'])
@login_required
def post_overview_survey():
    survey_shortname = request.form.get('overview-survey-choice')
    session['overview_survey'] = survey_shortname
    return redirect(url_for('home_bp.home'))


def format_data_for_template(collection_exercise, survey):
    """
    Takes various sets of data and formats them into an easy format for the template to display
    :param collection_exercise: A dictionary containing information on the most recent collection exercise
    :param survey: A dictionary containing information on the survey
    :return: A dictionary containing all the data needed for the overview template.
    """
    sample_data = get_sample_data(collection_exercise, survey)

    reference_info = {
        'exerciseRef': collection_exercise.get('exerciseRef'),
        'userDescription': collection_exercise.get('userDescription'),
        'survey_id': survey['surveyRef'],
        'shortName': survey['shortName'],
        'longName': survey['longName'],
    }
    formatted_dict = {**sample_data, **reference_info}

    # We can't be certain of what events are present so we need to handle it a little differently
    event_dict = convert_event_list_to_dictionary(collection_exercise.get('events'))
    variable_list = ['mps', 'go_live', 'return_by', 'exercise_end',
                     'period_start_date', 'period_end_date', 'employment_date']
    for item in variable_list:
        formatted_dict[item] = event_dict.get(item, 'N/A')

    return formatted_dict


def get_sample_data(collection_exercise, survey):
    """
    Generates a dict for the template so it's easy to display the data on the screen.
    :param collection_exercise: A dict containing data for the collection exercise.
    :param survey: A dict containing data on the survey.
    :return: A dict with the sample data in an easy to digest format.
    :rtype: dict
    """
    try:
        dashboard_url = f'{app.config["DASHBOARD_URL"]}/dashboard/collection-exercise/{collection_exercise["id"]}'
    except KeyError:
        dashboard_url = 'N/A'
    try:
        dashboard_data = collection_exercise_controllers.download_dashboard_data(
            collection_exercise['id'], survey['id'])
        sample_data = {
            'completed': dashboard_data.get('completed', 'N/A'),
            'sample_size': dashboard_data.get('sampleSize', 'N/A'),
            'not_started': dashboard_data.get('notStarted', 'N/A'),
            'in_progress': dashboard_data.get('inProgress', 'N/A'),
            'dashboard_url': dashboard_url
        }
    except (ApiError, ConnectionError, HTTPError, KeyError):
        logger.error("Failed to get dashboard data", collection_exercise_id=collection_exercise.get('id'))
        sample_data = {
            'completed': 'N/A',
            'sample_size': 'N/A',
            'not_started': 'N/A',
            'in_progress': 'N/A',
            'dashboard_url': dashboard_url
        }
    return sample_data
