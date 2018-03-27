import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError, UpdateContactDetailsException
from response_operations_ui.forms import EditContactDetailsForm

logger = wrap_logger(logging.getLogger(__name__))


def get_contact_details(respondent_id):
    logger.debug('Retrieving contact details by id', id=respondent_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/party-details'

    param = {"respondent_party_id": respondent_id}
    response = requests.get(url, params=param)

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved contact details', id=respondent_id)

    return response.json().get("respondent_party")


def update_contact_details(ru_ref, respondent_id, form):

    new_contact_details = {
        "first_name": form.get('first_name'),
        "last_name": form.get('last_name'),
        "email_address": form.get('hidden_email'),
        "new_email_address": form.get('email'),
        "telephone": form.get('telephone'),
        "respondent_id": respondent_id}

    old_contact_details = get_contact_details(respondent_id)
    contact_details_changed = _compare_contact_details(new_contact_details, old_contact_details)

    if len(contact_details_changed) > 0:
        url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/update-respondent-details/{respondent_id}'
        response = requests.put(url, json=new_contact_details)

        if response.status_code != 200:
            raise UpdateContactDetailsException(ru_ref, EditContactDetailsForm(form),
                                                old_contact_details, response.status_code)

        logger.debug('Respondent details updated', respondent_id=respondent_id, status_code=response.status_code)

    return contact_details_changed


def _compare_contact_details(new_contact_details, old_contact_details):

    # Currently the 'get contact details' and 'update respondent details' keys do not match and must be mapped
    contact_details_map = {
        "firstName": "first_name",
        "lastName": "last_name",
        "telephone": "telephone",
        "emailAddress": "new_email_address"}
    details_different = []

    for key in contact_details_map:
        if old_contact_details.get(key) != new_contact_details.get(contact_details_map[key]):
            details_different.append(key)

    return details_different
