import logging

from flask import abort
import requests
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui import app

logger = wrap_logger(logging.getLogger(__name__))


def sign_in(sign_in_data):
    logger.debug('Retrieving sign in authorisation')
    url = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'

    response = requests.post(url, json=sign_in_data)

    try:
        response.raise_for_status()
    except HTTPError as e:
        if e.response.status_code == 401:
            abort(401)
        else:
            raise e

    logger.debug('Successfully signed in')
    return response.json()
