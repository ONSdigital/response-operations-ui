import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_surveys_list():
    logger.debug('Retrieving surveys list')
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/surveys'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved surveys list')
    return response.json()


def get_survey(short_name):
    logger.debug('Retrieving survey', short_name=short_name)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname/{short_name}'

    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved survey', short_name=short_name)
    return response.json()


def get_surveys_dict():
    surveys_list = get_surveys_list()
    return {survey['id']: survey for survey in surveys_list}


def get_survey_short_name_by_id(survey_id):
    try:
        survey_short_name = app.surveys_dict[survey_id]['shortName']
    except (AttributeError, KeyError):
        try:
            app.surveys_dict = get_surveys_dict()
            survey_short_name = app.surveys_dict[survey_id]['shortName']
        except AttributeError:
            survey_short_name = 'Unavailable'
        except KeyError:
            logger.exception("Failed to resolve survey short name", survey_id=survey_id)
            survey_short_name = 'Unavailable'
    return survey_short_name
