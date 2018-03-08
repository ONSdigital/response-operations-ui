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
    # TODO cache this dictionary in app
    surveys_list = get_surveys_list()
    return {survey['id']: survey for survey in surveys_list}


def get_survey_short_name_by_id(survey_id):
    try:
        return get_surveys_dict()[survey_id]['shortName']
    except KeyError:
        logger.exception("failed to resolve survey short name", survey_id=survey_id)
        return 'Unavailable'
