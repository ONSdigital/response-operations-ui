import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def edit_contact_details(edit_details_data, respondent_id):
    logger.debug('Editing contact details', respondent_id=respondent_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/update-respondent-details/{respondent_id}'

    response = requests.put(url, json=edit_details_data)
    if response.status_code != 200:
        logger.debug('Error changing contact details', respondent_id=respondent_id)
        return False

    logger.debug('Successfully changed contact details', respondent_id=respondent_id)
    return True


def get_contact_details(respondent_id):
    logger.debug('Retrieving contact details by id', id=respondent_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/party-details'

    param = {"respondent_party_id": respondent_id}
    response = requests.get(url, params=param)

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved contact details', id=respondent_id)

    return response.json().get("respondent_party")
