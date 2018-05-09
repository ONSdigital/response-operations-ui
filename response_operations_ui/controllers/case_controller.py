import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_available_case_group_statuses(short_name, period, ru_ref):
    logger.debug('Retrieving case group status', short_name=short_name, period=period, ru_ref=ru_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/{short_name}/{period}/{ru_ref}'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved case group status', short_name=short_name, period=period, ru_ref=ru_ref)
    return response.json()


def update_case_group_statuses(short_name, period, ru_ref, event):
    logger.debug('Updating case group status', short_name=short_name, period=period, ru_ref=ru_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/{short_name}/{period}/{ru_ref}'
    response = requests.post(url, json={'event': event})
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully updated case group status', short_name=short_name, period=period, ru_ref=ru_ref)


def get_available_case_group_statuses_direct(collection_exercise_id, ru_ref):
    logger.debug('Retrieving statuses', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    url = f'{app.config["CASE_URL"]}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'
    response = requests.get(url, auth=app.config['CASE_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.debug('No statuses found', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
            return []
        logger.error('Error retrieving statuses', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
        raise ApiError(response)

    logger.debug('Successfully retrieved statuses', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    return response.json()


def get_case_groups_by_business_party_id(business_party_id):
    logger.debug('Retrieving case groups', party_id=business_party_id)
    url = f'{app.config["CASE_URL"]}/casegroups/partyid/{business_party_id}'
    response = requests.get(url, auth=app.config["CASE_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 204:
            logger.debug('No case groups found for business', party_id=business_party_id)
            return []
        logger.error('Failed to retrieve case groups', business_party_id=business_party_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved case groups', business_party_id=business_party_id)
    return response.json()


def get_cases_by_business_party_id(business_party_id):
    logger.debug('Retrieving cases', business_party_id=business_party_id)
    url = f'{app.config["CASE_URL"]}/cases/partyid/{business_party_id}'
    response = requests.get(url, auth=app.config['CASE_AUTH'], params={"iac": "True"})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404 or response.status_code == 204:
            logger.debug('No cases found for business', business_party_id=business_party_id)
            return []
        logger.error('Error retrieving cases', business_party_id=business_party_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved cases', business_party_id=business_party_id)
    return response.json()
