import logging

import requests
from flask import current_app as app
from requests import HTTPError
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def search_reporting_units(query, limit, page):
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/search'
    response = requests.get(
        url,
        params={"query": query, "page": page, "limit": limit},
        auth=app.config["BASIC_AUTH"],
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error("Error retrieving reporting units by search query", query=query, page=page, limit=limit)
        raise ApiError(response)

    return response.json()


def change_enrolment_status(business_id, respondent_id, survey_id, change_flag):
    logger.info(
        "Changing enrolment status",
        business_id=business_id,
        respondent_id=respondent_id,
        survey_id=survey_id,
        change_flag=change_flag,
    )
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/change_enrolment_status'
    enrolment_json = {
        "respondent_id": respondent_id,
        "business_id": business_id,
        "survey_id": survey_id,
        "change_flag": change_flag,
    }
    response = requests.put(url, json=enrolment_json, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error(
            "Failed to change enrolment status",
            business_id=business_id,
            respondent_id=respondent_id,
            survey_id=survey_id,
            change_flag=change_flag,
        )
        raise ApiError(response)

    logger.info(
        "Successfully changed enrolment status",
        business_id=business_id,
        respondent_id=respondent_id,
        survey_id=survey_id,
        change_flag=change_flag,
    )


def change_respondent_status(respondent_id, change_flag):
    if change_flag == "ACTIVE":
        logger.info("Changing respondent status", respondent_id=respondent_id, change_flag=change_flag)
        url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/edit-account-status/{respondent_id}'
        enrolment_json = {"respondent_id": respondent_id, "status_change": change_flag}
        response = requests.put(url, json=enrolment_json, auth=app.config["BASIC_AUTH"])

        try:
            response.raise_for_status()
        except HTTPError:
            logger.error("Failed to change respondent status", respondent_id=respondent_id, change_flag=change_flag)
            raise ApiError(response)

        logger.info("Successfully changed respondent status", respondent_id=respondent_id, change_flag=change_flag)
    else:
        logger.error("Incorrect change_flag given", respondent_id=respondent_id, change_flag=change_flag)
        raise ValueError("Incorrect change_flag given")


def generate_new_enrolment_code(case_id):
    """Generates a new enrolment code from a case id by hitting the case service

    :param case_id: A case_id
    """
    logger.info("Generating new enrolment code", case_id=case_id)
    url = f'{app.config["CASE_URL"]}/cases/{case_id}/events'
    case_event = {
        "description": "Generating new enrolment code",
        "category": "GENERATE_ENROLMENT_CODE",
        "subCategory": None,
        "createdBy": "ROPS",
    }

    response = requests.post(url, json=case_event, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error("Failed to generate new enrolment code", case_id=case_id)
        raise ApiError(response)

    logger.info("Successfully generated new enrolment code", case_id=case_id)
