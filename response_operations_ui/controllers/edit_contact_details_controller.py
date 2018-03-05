import logging

from flask import abort
import requests
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def edit_contact_details(edit_details_data):
    logger.debug('Validating contact details')
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/update-respondent-details'

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


def get_contact_details(respondent_id):
    logger.debug('Retrieving contact details by id', id=respondent_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/party-details'

    param = {"respondent_party_id": respondent_id}
    response = requests.get(url, params=param)

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Succesfully retrieved contact details', id=respondent_id)

    return response.json().get("respondent_party")
