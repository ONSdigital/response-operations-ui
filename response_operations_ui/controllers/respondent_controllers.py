import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def search_respondent_by_email(email):
    logger.debug('Search respondent via email')

    request_json = {
        'email': email
    }
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/get-respondent-by-email'
    response = requests.get(url, json=request_json)

    if response.status_code == 404:
        return response.json()

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Respondent retrieval failed")
        raise ApiError(response)
    logger.debug("Respondent retrieved successfully")

    return response.json()
