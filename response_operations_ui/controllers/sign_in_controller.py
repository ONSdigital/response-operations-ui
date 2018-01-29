import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def sign_in(sign_in_data):
    logger.debug('Retrieving sign in authorisation')
    url = f'{app.config["BACKSTAGE_API_URL"]}/sign-in'

    response = requests.post(url, json=sign_in_data)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully signed in')
    return response.json()
