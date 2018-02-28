import logging

from flask import abort
import requests
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui import app

logger = wrap_logger(logging.getLogger(__name__))


def edit_contact_details(edit_details_data):
    logger.debug('Validating contact details')
    # TODO: Add in correct url from backstage
    url = f'{app.config["BACKSTAGE_API_URL"]}/'

    response = requests.post(url, json=edit_details_data)

    try:
        response.raise_for_status()
    except HTTPError as e:
        if e.response.status_code == 401:
            abort(401)
        else:
            raise e

    logger.debug('Successfully changed contact details')
    return response.json()
