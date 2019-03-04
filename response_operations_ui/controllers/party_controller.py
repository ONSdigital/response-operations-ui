import os

import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.exceptions.exceptions import UpdateContactDetailsException
from response_operations_ui.exceptions.exceptions import SearchRespondentsException
from response_operations_ui.forms import EditContactDetailsForm
from response_operations_ui.controllers.mock_party_controller import mock_search_respondents


logger = wrap_logger(logging.getLogger(__name__))


def get_party_by_ru_ref(ru_ref):
    logger.debug('Retrieving reporting unit', ru_ref=ru_ref)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/parties/type/B/ref/{ru_ref}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Failed to retrieve reporting unit', ru_ref=ru_ref)
        raise ApiError(response)

    logger.debug('Successfully retrieved reporting unit', ru_ref=ru_ref)
    return response.json()


def get_business_by_party_id(business_party_id, collection_exercise_id=None):
    logger.debug('Retrieving business party',
                 business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/id/{business_party_id}'
    params = {"collection_exercise_id": collection_exercise_id, "verbose": True}
    response = requests.get(url, params=params, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error retrieving business party',
                  business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved business party',
                 business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
    return response.json()


def get_respondent_by_party_id(respondent_party_id):
    logger.debug('Retrieving respondent party', respondent_party_id=respondent_party_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_party_id}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error retrieving respondent party', respondent_party_id=respondent_party_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved respondent party', respondent_party_id=respondent_party_id)
    return response.json()


def survey_ids_for_respondent(respondent, ru_ref):
    enrolments = [association.get('enrolments')
                  for association in respondent.get('associations')
                  if association['sampleUnitRef'] == ru_ref][0]
    return [enrolment.get('surveyId') for enrolment in enrolments]


def add_enrolment_status_to_respondent(respondent, ru_ref, survey_id):
    association = next((association
                        for association in respondent.get('associations')
                        if association['sampleUnitRef'] == ru_ref), None)
    enrolment_status = next((enrolment['enrolmentStatus']
                             for enrolment in association.get('enrolments')
                             if enrolment['surveyId'] == survey_id), None)
    return {**respondent, 'enrolmentStatus': enrolment_status}


def get_respondent_enrolments(respondent, enrolment_status=None):

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
        log_level = logger.warning if response.status_code == 400 else logger.exception
        log_level("Respondent retrieval failed")
        raise ApiError(response)
    logger.debug("Respondent retrieved successfully")

    return response.json()


def search_respondents(first_name, last_name, email_address, page=0):
    if bool(os.environ.get('FAKE_PARTY_DATA', False)):
        logger.debug('Respondent Search: Using fake data for controller')
        data = mock_search_respondents(first_name, last_name, email_address, page)
    else:
        url = _get_search_respondents_url(first_name=first_name,
                                          last_name=last_name,
                                          email_address=email_address,
                                          page=page)
        response = requests.get(url, auth=app.config['PARTY_AUTH'])
        if response.status_code != 200:
            raise SearchRespondentsException(response,
                                             first_name=first_name,
                                             last_name=last_name,
                                             email_address=email_address,
                                             page=page)
        data = response.json()

    return data


def _get_search_respondents_url(**kwargs):
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents?'

    # Dict provides translation of variable names in response ops to url param names in party
    kw_to_url_params = {
        'first_name': 'firstName',
        'last_name': 'lastName',
        'email_address': 'email',
        'page': 'page'
    }

    for resops_name, party_name in kw_to_url_params:
        arg = kwargs.get(resops_name)
        if arg and arg != '':
            url += f'{party_name}={arg}&'

    url += f'limit={app.config["PARTY_RESPONDENTS_PER_PAGE"]}'

    return url


def update_contact_details(respondent_id, form, ru_ref='NOT DEFINED'):
    logger.debug('Updating respondent details', respondent_id=respondent_id)

    new_contact_details = {
        "firstName": form.get('first_name'),
        "lastName": form.get('last_name'),
        "email_address": form.get('hidden_email'),
        "new_email_address": form.get('email'),
        "telephone": form.get('telephone')
    }

    old_contact_details = get_respondent_by_party_id(respondent_id)
    contact_details_changed = _compare_contact_details(new_contact_details, old_contact_details)

    if len(contact_details_changed) > 0:
        url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_id}'
        response = requests.put(url, json=new_contact_details, auth=app.config['PARTY_AUTH'])

        if response.status_code != 200:
            raise UpdateContactDetailsException(ru_ref, EditContactDetailsForm(form),
                                                old_contact_details, response.status_code)

        logger.debug('Respondent details updated', respondent_id=respondent_id, status_code=response.status_code)

    return contact_details_changed


def _compare_contact_details(new_contact_details, old_contact_details):
    # Currently the 'get contact details' and 'update respondent details' keys do not match and must be mapped
    contact_details_map = {
        "firstName": "firstName",
        "lastName": "lastName",
        "telephone": "telephone",
        "emailAddress": "new_email_address"}

    return {old_key for old_key, new_key in contact_details_map.items()
            if old_contact_details[old_key] != new_contact_details[new_key]}
