import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_reporting_unit(ru_ref):
    logger.debug('Retrieving reporting unit', ru_ref=ru_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/{ru_ref}'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved reporting unit', ru_ref=ru_ref)
    return response.json()


def search_reporting_units(query):
    logger.debug('Retrieving reporting units by search query', query=query)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/search'
    response = requests.get(url, params={'query': query})

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved reporting units by search', query=query)

    return response.json()


def generate_new_enrolment_code(collection_exercise_id, ru_ref):
    logger.debug('Generating new enrolment code', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/iac/{collection_exercise_id}/{ru_ref}'
    response = requests.post(url)

    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully generated new enrolment code',
                 collection_exercise_id=collection_exercise_id,
                 ru_ref=ru_ref)
    return response.json()


def resend_verification_email(party_id):
    logger.debug('Re-sending verification email', party_id=party_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/resend-verification-email/{party_id}'

    response = requests.post(url)
    if response.status_code != 200:
        logger.exception("Re-sending of verification email failed", party_id=party_id)
        raise ApiError(response)

    logger.info('Successfully re-sent verification email', party_id=party_id)
