import logging

import requests
from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_case_by_id(case_id):
    logger.info("Retrieving case", case_id=case_id)
    url = f'{app.config["CASE_URL"]}/cases/{case_id}?iac=true'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Error retrieving case", case_id=case_id)
        raise ApiError(response)

    logger.info("Successfully retrieved case", case_id=case_id)
    return response.json()


def post_case_event(case_id, category, description):
    logger.info("Posting case event", case_id=case_id, category=category)
    url = f'{app.config["CASE_URL"]}/cases/{case_id}/events'
    case_event = {"category": category, "description": description, "createdBy": "ROPS"}
    response = requests.post(url, auth=app.config["BASIC_AUTH"], json=case_event)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Error posting case event", case_id=case_id, category=category)
        raise ApiError(response)

    logger.info("Successfully posted case event", case_id=case_id, category=category)


def get_case_by_case_group_id(case_group_id):
    logger.info("Retrieving case by case group id", case_group_id=case_group_id)
    url = f'{app.config["CASE_URL"]}/cases/casegroupid/{case_group_id}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Error getting case by case group id", case_group_id=case_group_id)
        raise ApiError(response)

    logger.info("Successfully retrieved case by case group id", case_group_id=case_group_id)
    return response.json()[0]


def get_available_case_group_statuses_direct(collection_exercise_id, ru_ref):
    logger.info("Retrieving statuses", collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    url = f'{app.config["CASE_URL"]}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.info("No statuses found", collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
            return {}
        logger.exception("Error retrieving statuses", collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
        raise ApiError(response)

    logger.info("Successfully retrieved statuses", collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    return response.json()


def get_case_groups_by_business_party_id(business_party_id):
    logger.info("Retrieving case groups", party_id=business_party_id)
    url = f'{app.config["CASE_URL"]}/casegroups/partyid/{business_party_id}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
        if response.status_code == 204:
            logger.info("No case groups found for business", party_id=business_party_id)
            return []
    except requests.exceptions.HTTPError:
        logger.exception("Failed to retrieve case groups", business_party_id=business_party_id)
        raise ApiError(response)

    logger.info("Successfully retrieved case groups", business_party_id=business_party_id)
    return response.json()


def get_cases_by_business_party_id(business_party_id):
    logger.info("Retrieving cases", business_party_id=business_party_id)
    url = f'{app.config["CASE_URL"]}/cases/partyid/{business_party_id}'
    response = requests.get(
        url,
        auth=app.config["BASIC_AUTH"],
        params={"iac": "True", "max_cases_per_survey": app.config["MAX_CASES_RETRIEVED_PER_SURVEY"]},
    )

    try:
        response.raise_for_status()
        if response.status_code == 204:
            logger.info("No cases found for business", business_party_id=business_party_id)
            return []
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.info("No cases found for business", business_party_id=business_party_id)
            return []
        logger.exception("Error retrieving cases", business_party_id=business_party_id)
        raise ApiError(response)

    logger.info("Successfully retrieved cases", business_party_id=business_party_id)
    return response.json()


def get_case_group_by_collection_exercise(case_groups, collection_exercise_id):
    return next(
        (case_group for case_group in case_groups if case_group["collectionExerciseId"] == collection_exercise_id), None
    )


def get_iac_url(case_id):
    return f'{app.config["CASE_URL"]}/cases/{case_id}/iac'


def generate_iac(case_id):
    url = get_iac_url(case_id)
    logger.info("Generating new IAC", case_id=case_id, url=url)

    response = requests.post(url=url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.exception("Error generating IAC", case_id=case_id)
        raise ApiError(response)

    return response.json()["iac"]


def get_case_events_by_case_id(case_id, categories=None):
    logger.info("Retrieving cases", case_id=case_id)
    url = f'{app.config["CASE_URL"]}/cases/{case_id}/events'
    if isinstance(categories, list):
        url = url + "?category=" + ",".join(categories)
    elif categories:
        url = url + "?category=" + categories

    response = requests.get(url, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.info("No statuses found", case_id=case_id)
            return {}
        logger.exception("Error retrieving statuses", case_id=case_id)
        raise ApiError(response)
    logger.info("Successfully retrieved statuses", case_id=case_id)
    return response.json()
