import logging
import time

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from config import FDI_LIST, VACANCIES_LIST
from response_operations_ui.common.mappers import format_short_name
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def check_cache():
    logger.debug("checking cache age")
    # if the cache is greater than 60 seconds refresh it
    if not hasattr(app, "surveys_dict_time") or time.monotonic() - app.surveys_dict_time > 60:
        logger.debug("cache older than 60 seconds refreshing")
        try:
            refresh_cache()
        except ApiError:
            logger.exception("Failed to refresh survey cache")
    else:
        logger.debug("cache is not out of date")


def refresh_cache():
    logger.debug("refreshing cache")
    app.surveys_dict = get_surveys_dictionary()
    app.surveys_dict_time = time.monotonic()
    logger.debug("refreshed cache")


def get_survey_by_id(survey_id):
    """
    Gets a survey from the survey service by its uuid.  This uuid is the one assigned
    to the survey when it was created

    :param survey_id: A uuid for a survey
    :type survey_id: str
    :return: A dict containing the json describing the survey
    :rtype: dict
    """
    logger.info("Retrieve survey using survey uuid", survey_id=survey_id)
    url = f'{app.config["SURVEY_URL"]}/surveys/{survey_id}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Survey retrieval failed", survey_id=survey_id)
        raise ApiError(response)

    logger.info("Successfully retrieved survey", survey_id=survey_id)
    return response.json()


def get_survey_by_ref(survey_id):
    """
    Gets a survey from the service service by its id.  This id is the one the ONS refers to the survey
    by (e.g., MBS = 009, RSI = 023)

    :param survey_id: A number representing the id of the survey
    :type survey_id: str
    :return: A dict containing the json describing the survey
    :rtype: dict
    """
    logger.info("Retrieve survey using survey id", survey_id=survey_id)
    url = f'{app.config["SURVEY_URL"]}/surveys/ref/{survey_id}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Survey retrieval failed", survey_id=survey_id)
        raise ApiError(response)

    logger.info("Successfully retrieved survey", survey_id=survey_id)
    return response.json()


def get_survey_by_shortname(short_name: str) -> dict:
    short_name = "".join(short_name.split())
    logger.info("Retrieving survey", short_name=short_name)
    url = f'{app.config["SURVEY_URL"]}/surveys/shortname/{short_name}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Error retrieving survey", short_name=short_name)
        raise ApiError(response)

    logger.info("Successfully retrieved survey", short_name=short_name)
    return response.json()


def get_surveys_list():
    logger.info("Retrieving surveys list")
    url = f'{app.config["SURVEY_URL"]}/surveys/surveytype/Business'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    if response.status_code == 204:
        logger.info("No surveys found in survey service")
        return []

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error("Error retrieving the survey list")
        raise ApiError(response)

    logger.info("Successfully retrieved surveys list")
    survey_list = response.json()
    # Format survey shortName
    for survey in survey_list:
        survey["shortName"] = format_short_name(survey["shortName"])
    # Order List by surveyRef
    return sorted(survey_list, key=lambda k: k["surveyRef"])


def get_survey(short_name: str) -> dict:
    survey = get_survey_by_shortname(short_name)
    logger.info("Getting survey details", short_name=short_name, survey_id=survey["id"])

    # Format survey shortName
    survey["shortName"] = format_short_name(survey["shortName"])

    logger.info("Successfully retrieved survey details", short_name=short_name, survey_id=survey["id"])
    return survey


def convert_specific_surveys_to_specific_shortnames(survey_short_name: str) -> str:
    for fdi_survey in FDI_LIST:
        if survey_short_name == fdi_survey:
            return "FDI"
    for vacancies_survey in VACANCIES_LIST:
        if survey_short_name == vacancies_survey:
            return "Vacancies"
    return survey_short_name


def get_surveys_dictionary() -> dict:
    surveys_list = get_surveys_list()
    return {
        survey["id"]: {
            "shortName": convert_specific_surveys_to_specific_shortnames(survey.get("shortName")),
            "surveyRef": survey.get("surveyRef"),
        }
        for survey in surveys_list
    }


def get_grouped_surveys_list() -> set:
    """
    Returns a set of survey names.  Certain groups of similar surveys will be grouped together under a single name
    (i.e., AOFDI, AIFDI, QIFDI and QOFDI will be absent and instead there will be one FDI entry)

    :return: A set of survey shortnames
    """
    survey_set = {convert_specific_surveys_to_specific_shortnames(survey["shortName"]) for survey in get_surveys_list()}
    return sorted(survey_set)


def get_business_survey_shortname_list() -> set:
    """
    Returns a set of survey names.  This is different from `get_grouped_surveys_list` as it gives you all of them
    without any filtering.

    :return: A set of survey shortnames
    """
    survey_set = {survey["shortName"] for survey in get_surveys_list()}
    return sorted(survey_set)


def get_survey_short_name_by_id(survey_id: str) -> str:
    try:
        check_cache()
        return app.surveys_dict[survey_id]["shortName"]
    except (AttributeError, KeyError):
        try:
            # force a refresh in case there's a new survey
            refresh_cache()
            return app.surveys_dict[survey_id]["shortName"]
        except ApiError:
            logger.exception("Failed to resolve survey short name due to API error", survey_id=survey_id)
        except KeyError:
            logger.exception("Failed to resolve survey short name", survey_id=survey_id)


def get_survey_id_by_short_name(short_name: str) -> str:
    """
    Returns the uuid of the survey by querying the survey service using the survey's shortname.

    :param short_name: The survey's shortname
    :return: The survey's uuid
    """
    logger.info("Retrieving survey id by short name", short_name=short_name)
    return get_survey_by_shortname(short_name)["id"]


def get_survey_ref_by_id(survey_id: str):
    try:
        check_cache()
        return app.surveys_dict[survey_id]["surveyRef"]
    except (AttributeError, KeyError):
        try:
            # force a refresh in case there's a new survey
            refresh_cache()
            return app.surveys_dict[survey_id]["surveyRef"]
        except ApiError:
            logger.exception("Failed to resolve survey ref due to API error", survey_id=survey_id)
        except KeyError:
            logger.exception("Failed to resolve survey ref", survey_id=survey_id)


def update_survey_details(survey_ref, short_name, long_name, survey_mode):
    logger.info("Updating survey details", survey_ref=survey_ref)
    url = f'{app.config["SURVEY_URL"]}/surveys/ref/{survey_ref}'

    survey_details = {"ShortName": short_name, "LongName": long_name, "surveyMode": survey_mode}
    response = requests.put(url, json=survey_details, auth=app.config["BASIC_AUTH"])

    if response.status_code == 404:
        logger.warning("Error retrieving survey details", survey_ref=survey_ref)
        raise ApiError(response)
    try:
        response.raise_for_status()
    except HTTPError:
        logger.error("Failed to update survey details", survey_ref=survey_ref)
        raise ApiError(response)

    logger.info("Successfully updated survey details", survey_ref=survey_ref)


def get_legal_basis_list():
    logger.info("Retrieving legal basis list")
    url = f'{app.config["SURVEY_URL"]}/legal-bases'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error("Failed retrieving legal basis list")
        raise ApiError(response)

    lbs = [(lb["ref"], lb["longName"]) for lb in response.json()]
    logger.info("Successfully retrieved legal basis list")
    return lbs


def create_survey(survey_ref, short_name, long_name, legal_basis, survey_mode):
    logger.info(
        "Creating new survey",
        survey_ref=survey_ref,
        short_name=short_name,
        long_name=long_name,
        legal_basis=legal_basis,
        survey_mode=survey_mode,
    )
    url = f'{app.config["SURVEY_URL"]}/surveys'

    survey_details = {
        "surveyRef": survey_ref,
        "shortName": short_name,
        "longName": long_name,
        "legalBasisRef": legal_basis,
        "surveyType": "Business",
        "surveyMode": survey_mode,
        "classifiers": [
            {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["FORM_TYPE"]},
            {"name": "COMMUNICATION_TEMPLATE", "classifierTypes": ["LEGAL_BASIS", "REGION"]},
        ],
        "eqVersion": "v3" if survey_mode != "SEFT" else "",
    }
    response = requests.post(url, json=survey_details, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Error creating new survey",
            survey_ref=survey_ref,
            short_name=short_name,
            long_name=long_name,
            legal_basis=legal_basis,
            survey_mode=survey_mode,
            status_code=response.status_code,
        )
        raise ApiError(response)

    logger.info("Successfully created new survey", survey_ref=survey_ref)
