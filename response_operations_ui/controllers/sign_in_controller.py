import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app

logger = wrap_logger(logging.getLogger(__name__))


def sign_in(sign_in_data):
    logger.debug('Retrieving sign in authorisation')
    url = f'{app.config["BACKSTAGE_API_URL"]}/sign-in-uaa'

    response = requests.post(url, json=sign_in_data)
    return response.json()
