import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_party_by_ru_ref(ru_ref):
    logger.debug('Retrieving reporting unit', ru_ref=ru_ref)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/parties/type/B/ref/{ru_ref}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve reporting unit', ru_ref=ru_ref)
        raise ApiError(response)

    logger.debug('Successfully retrieved reporting unit', ru_ref=ru_ref)
    return response.json()


def get_business_party_by_party_id(business_party_id, collection_exercise_id=None):
    logger.debug('Retrieving business party',
                 business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/id/{business_party_id}'
    params = {"collection_exercise_id": collection_exercise_id, "verbose": True}
    response = requests.get(url, params=params, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Error retrieving business party',
                     business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved business party',
                 business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
    return response.json()


def get_respondent_party_by_party_id(respondent_party_id):
    logger.debug('Retrieving respondent party', respondent_party_id=respondent_party_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_party_id}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Error retrieving respondent party', respondent_party_id=respondent_party_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved respondent party', respondent_party_id=respondent_party_id)
    return response.json()


def survey_ids_for_respondent(respondent, ru_ref):
    enrolments = [association.get('enrolments')
                  for association in respondent.get('associations')
                  if association['sampleUnitRef'] == ru_ref][0]
    return [enrolment.get('surveyId') for enrolment in enrolments]


def add_enrolment_status_to_respondent(respondent, ru_ref, survey_id):
    association = next(association
                       for association in respondent.get('associations')
                       if association['sampleUnitRef'] == ru_ref)
    enrolment_status = next(enrolment['enrolmentStatus']
                            for enrolment in association.get('enrolments')
                            if enrolment['surveyId'] == survey_id)
    return {**respondent, 'enrolmentStatus': enrolment_status}
