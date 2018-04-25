import logging
import requests

from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_business_by_party_id(party_id):
    logger.debug("Get business details")
    url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/businesses/id/{party_id}'
    response = requests.get(url, auth=app.config['BASIC_AUTH'])

    if response.status_code != 200:
        raise ApiError(response)

    return response.json()


def get_respondent_by_party_id(party_id):
    logger.debug("Get respondent details")
    url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/id/{party_id}'
    response = requests.get(url=url, auth=app.config['BASIC_AUTH'])

    if response.status_code != 200:
        raise ApiError(response)

    return response.json()


def get_respondent_enrolments(party_id, enrolment_status=None):
    logger.debug("Get respondent enrolment details")

    respondent_details = get_respondent_by_party_id(party_id)

    enrolments = []
    for association in respondent_details['associations']:
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


def change_respondent_account_status(party_id, status_change):
    logger.debug('Changing respondent account status', party_id=party_id, status_change=status_change)
    url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/edit-account-status/{party_id}'
    response = requests.put(url, auth=app.config['BASIC_AUTH'], json={'status_change': status_change})

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully changed respondent account status', party_id=party_id, status_change=status_change)


def search_respondent_by_email(email):
    logger.debug('Search respondent via email')

    request_json = {
        'email': email
    }
    url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/email'
    response = requests.get(url, json=request_json, auth=app.config['BASIC_AUTH'])

    if response.status_code == 404:
        return response.json()

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Respondent retrieval failed")
        raise ApiError(response)
    logger.debug("Respondent retrieved successfully")

    return response.json()
