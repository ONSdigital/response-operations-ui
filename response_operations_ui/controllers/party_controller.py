import logging

import requests
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.exceptions.exceptions import ApiError, UpdateContactDetailsException
from response_operations_ui.forms import EditContactDetailsForm

logger = wrap_logger(logging.getLogger(__name__))


def get_respondent_by_party_id(party_id):
    logger.debug("Get respondent details")
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{party_id}'
    response = requests.get(url=url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        logger.exception("Respondent retrieval failed", party_id=party_id)
        raise ApiError(response)

    return response.json()


def get_business_by_party_id(party_id):
    logger.debug("Get business details")
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/id/{party_id}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        logger.exception("Business retrieval failed", party_id=party_id)
        raise ApiError(response)

    return response.json()


def get_respondent_enrolments(respondent, enrolment_status=None):
    logger.debug("Get respondent enrolment details")

    enrolments = []
    for association in respondent['associations']:
        business_party = get_business_by_party_id(association['partyId'])
        for enrolment in association['enrolments']:
            enrolment_data = {
                "business": business_party,
                "survey": get_survey_by_id(enrolment['surveyId']),
                "status": enrolment['enrolmentStatus']
            }
            if enrolment_status:
                if enrolment_data['status'] == enrolment_status:
                    enrolments.append(enrolment_data)
            else:
                enrolments.append(enrolment_data)
    return enrolments


def search_respondent_by_email(email):
    logger.debug('Search respondent via email')

    request_json = {
        'email': email
    }
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/email'
    response = requests.get(url, json=request_json, auth=app.config['PARTY_AUTH'])

    if response.status_code == 404:
        return

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        logger.exception("Respondent retrieval failed")
        raise ApiError(response)
    logger.debug("Respondent retrieved successfully")

    return response.json()


def update_contact_details(ru_ref, respondent_id, form):

    new_contact_details = {
        "first_name": form.get('first_name'),
        "last_name": form.get('last_name'),
        "email_address": form.get('hidden_email'),
        "new_email_address": form.get('email'),
        "telephone": form.get('telephone'),
        "respondent_id": respondent_id}

    old_contact_details = get_respondent_by_party_id(respondent_id)
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
