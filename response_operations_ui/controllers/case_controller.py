import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_case_by_id(case_id):
    logger.debug('Retrieving case', case_id=case_id)
    url = f'{app.config["CASE_URL"]}/cases/{case_id}'
    response = requests.get(url, auth=app.config['CASE_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception('Error retrieving case', case_id=case_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved case', case_id=case_id)
    return response.json()


def update_case_group_status(collection_exercise_id, ru_ref, case_group_event):
    logger.debug('Updating status', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref,
                 case_group_event=case_group_event)
    url = f'{app.config["CASE_URL"]}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'
    response = requests.put(url, auth=app.config['CASE_AUTH'], json={'event': case_group_event})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception('Error updating case group status', collection_exercise_id=collection_exercise_id,
                         ru_ref=ru_ref, case_group_event=case_group_event)
        raise ApiError(response)

    logger.debug('Successfully updated case group status', collection_exercise_id=collection_exercise_id,
                 ru_ref=ru_ref, case_group_event=case_group_event)


def get_available_case_group_statuses_direct(collection_exercise_id, ru_ref):
    logger.debug('Retrieving statuses', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    url = f'{app.config["CASE_URL"]}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'
    response = requests.get(url, auth=app.config['CASE_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.debug('No statuses found', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
            return {}
        logger.exception('Error retrieving statuses', collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
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
        logger.exception('Failed to retrieve case groups', business_party_id=business_party_id)
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
        logger.exception('Error retrieving cases', business_party_id=business_party_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved cases', business_party_id=business_party_id)
    return response.json()


def is_allowed_status(status):
    allowed_statuses = {
        'COMPLETEDBYPHONE',
        'NOLONGERREQUIRED',
    }
    return status in allowed_statuses


def get_case_group_status_by_collection_exercise(case_groups, collection_exercise_id):
    return next((case_group['caseGroupStatus'] for case_group in case_groups
                 if case_group['collectionExerciseId'] == collection_exercise_id), None)
