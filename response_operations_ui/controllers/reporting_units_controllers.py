import logging

import requests
from flask import current_app as app
from structlog import wrap_logger

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


def change_respondent_status(respondent_id, change_flag):
    if change_flag == 'UNLOCKED':
        change_flag = 'ACTIVE'
        logger.debug('Changing respondent status', respondent_id=respondent_id, change_flag=change_flag)
        url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/edit-account-status/{respondent_id}'
        enrolment_json = {
            'respondent_id': respondent_id,
            'status_change': change_flag
        }
        response = requests.put(url, json=enrolment_json, auth=app.config['PARTY_AUTH'])

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.error('Failed to change respondent status', respondent_id=respondent_id, change_flag=change_flag)
            raise ApiError(response)

        logger.info('Successfully changed respondent status', respondent_id=respondent_id, change_flag=change_flag)


def generate_new_enrolment_code(case_id):
    logger.debug('Generating new enrolment code', case_id=case_id)
    url = f'{app.config["CASE_URL"]}/cases/{case_id}/events'
    case_event = {
        "description": "Generating new enrolment code",
        "category": "GENERATE_ENROLMENT_CODE",
        "subCategory": None,
        "createdBy": "ROPS"
    }

    response = requests.post(url, json=case_event, auth=app.config['CASE_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to generate new enrolment code', case_id=case_id)
        raise ApiError(response)

    logger.debug('Successfully generated new enrolment code', case_id=case_id)


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
