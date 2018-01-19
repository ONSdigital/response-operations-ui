import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_surveys_list():
    logger.debug('Retrieving surveys list')
    url = f'{app.config["BACKSTAGE_API_URL"]}/survey/surveys'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved surveys list')
    return response.json()


def get_survey(short_name):
    logger.debug('Retrieving survey', short_name=short_name)
    url = f'{app.config["BACKSTAGE_API_URL"]}/survey/shortname/{short_name}'

    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved survey', short_name=short_name)
    return response.json()
