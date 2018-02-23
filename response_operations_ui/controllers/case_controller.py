import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_available_case_group_statuses(short_name, period, ru_ref):
    logger.debug('Retrieving case group status', short_name=short_name, period=period, ru_ref=ru_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/{short_name}/{period}/{ru_ref}'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved case group status', short_name=short_name, period=period, ru_ref=ru_ref)
    return response.json()


def update_case_group_statuses(short_name, period, ru_ref, event):
    logger.debug('Updating case group status', short_name=short_name, period=period, ru_ref=ru_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/{short_name}/{period}/{ru_ref}'
    response = requests.post(url, json={'event': event})
    if response.status_code != 200:
        raise ApiError(response)
