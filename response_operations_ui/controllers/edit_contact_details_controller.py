import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def edit_contact_details(edit_details_data, respondent_id, respondent_details):
    logger.debug('Editing contact details', respondent_id=respondent_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/update-respondent-details/{respondent_id}'

    message = None

    response = requests.put(url, json=edit_details_data)
    if response.status_code == 200:
        logger.debug('Respondent details updated', respondent_id=respondent_id, status_code=response.status_code)

    if response.status_code == 409:
        #raise Exception:
        'Email address already exists'
    elif response.status_code == 404:
        details_changed_message = 'Connection error'
    else:
        details_changed_message = 'Connection error'

    logger.info(details_changed_message, status_code=response.status_code, respondent_id=respondent_id)

    details_changed = False
    email_changed = False

    if respondent_details.get("firstName") != edit_details_data.get("first_name"):
        details_changed = True
    elif respondent_details.get("lastName") != edit_details_data.get("last_name"):
        details_changed = True
    elif respondent_details.get("telephone") != edit_details_data.get("telephone"):
        details_changed = True
    if respondent_details.get('emailAddress') != edit_details_data.get("new_email_address"):
        email_changed = True

    if details_changed and email_changed:
        details_changed_message = f'Contact details saved and verification email sent to ' \
                                  f'{edit_details_data["new_email_address"]}'
    elif details_changed and not email_changed:
        details_changed_message = 'Contact details changed'
    elif email_changed:
        details_changed_message = f'Verification email sent to {edit_details_data["new_email_address"]}'

    return details_changed_message


def get_contact_details(respondent_id):
    logger.debug('Retrieving contact details by id', id=respondent_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/party-details'

    param = {"respondent_party_id": respondent_id}
    response = requests.get(url, params=param)

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved contact details', id=respondent_id)

    return response.json().get("respondent_party")
