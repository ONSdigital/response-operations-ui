import logging

import requests
from flask import current_app as app
from structlog import wrap_logger
from structlog.processors import JSONRenderer

from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__),
                     processors=[JSONRenderer(indent=1, sort_keys=True)])


def search_respondent_by_email(email):
    logger.info('Searching for respondent by email')

    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/email'
    response = requests.get(url, json={'email': email}, auth=app.config['PARTY_AUTH'])

    if response.status_code == 404:
        logger.info("No respondent found for email address", status_code=response.status_code)
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Respondent retrieval failed")
        raise ApiError(response)
    logger.info("Respondent retrieved by email successfully")

    return response.json()
