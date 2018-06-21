import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def search_reporting_units(query):
    logger.debug('Retrieving reporting units by search query', query=query)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/search'
    response = requests.get(url, params={'query': query}, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Error retrieving reporting units by search query', query=query)
        raise ApiError(response)

    logger.debug('Successfully retrieved reporting units by search', query=query)

    return response.json()


def change_enrolment_status(business_id, respondent_id, survey_id, change_flag):
    logger.debug('Changing enrolment status',
                 business_id=business_id, respondent_id=respondent_id, survey_id=survey_id, change_flag=change_flag)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/change_enrolment_status'
    enrolment_json = {
        'respondent_id': respondent_id,
        'business_id': business_id,
        'survey_id': survey_id,
        'change_flag': change_flag
    }
    response = requests.put(url, json=enrolment_json, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to change enrolment status',
                     business_id=business_id, respondent_id=respondent_id, survey_id=survey_id, change_flag=change_flag)
        raise ApiError(response)

    logger.debug('Successfully changed enrolment status',
                 business_id=business_id, respondent_id=respondent_id, survey_id=survey_id, change_flag=change_flag)


def generate_new_enrolment_code(collection_exercise_id, ru_ref):
    logger.debug('Generating new enrolment code', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    url = f'{app.config["CASE_URL"]}/cases/iac/{collection_exercise_id}/{ru_ref}'
    response = requests.post(url, auth=app.config['CASE_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to generate new enrolment code',
                     collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
        raise ApiError(response)

    logger.debug('Successfully generated new enrolment code',
                 collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    return response.json()


def resend_verification_email(party_id):
    logger.debug('Re-sending verification email', party_id=party_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/resend-verification-email/{party_id}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Re-sending of verification email failed", party_id=party_id)
        raise ApiError(response)

    logger.debug('Successfully re-sent verification email', party_id=party_id)
