import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_sample_summary(sample_summary_id):
    logger.info("Retrieving sample summary", sample_summary_id=sample_summary_id)
    url = f'{app.config["SAMPLE_URL"]}/samples/samplesummary/{sample_summary_id}'

    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Error retrieving sample summary", sample_summary_id=sample_summary_id, status_code=response.status_code
        )
        raise ApiError(response)

    logger.info("Successfully retrieved sample summary", sample_summary_id=sample_summary_id)
    return response.json()


def check_if_all_sample_units_present_for_sample_summary(sample_summary_id: str) -> dict:
    """
    Calls endpoint in sample that counts if expected sample units == actual number of sample units
    and changes sample summary state to ACTIVE if the two number do match.

    :param sample_summary_id:
    :return:
    """
    logger.info("Checking sample summary state", sample_summary_id=sample_summary_id)

    url = (
        f'{app.config["SAMPLE_URL"]}/samples/samplesummary/'
        f"{sample_summary_id}/check-and-transition-sample-summary-status"
    )
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Error checking sample summary", sample_summary_id=sample_summary_id, status_code=response.status_code

        )
        raise ApiError(response)

    response_json = response.json()
    are_all_sample_units_loaded = response_json["areAllSampleUnitsLoaded"]
    logger.info(
        "Successfully checked if all units present",
        sample_summary_id=sample_summary_id,
        are_all_sample_units_loaded=are_all_sample_units_loaded,
        expected_total=response_json["expectedTotal"],
        current_total=response_json["currentTotal"],
    )

    return response_json


def upload_sample(short_name, period, file):
    logger.info("Uploading sample", short_name=short_name, period=period, filename=file.filename)

    url = f'{app.config["SAMPLE_FILE_UPLOADER_URL"]}/samples/fileupload'

    response = requests.post(url=url, auth=app.config["BASIC_AUTH"], files={"file": file})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Error uploading sample file", status=response.status_code)
        raise ApiError(response)

    sample_summary = response.json()

    logger.info("Successfully uploaded sample file", response_json=sample_summary, sample_id=sample_summary["id"])

    return sample_summary


def delete_sample(sample_summary_id: str) -> None:
    """
    Deletes the sample summary and associated sample units that have been previously uploaded.
    In the case of getting a 404 from the sample service we'll just assume it's 'successful' as nothing is wrong,
    just that nothing got deleted.

    :param sample_summary_id: The sample summary uuid
    :return: None, as the sample service returns a 204 on success
    """
    logger.info("Deleting sample", sample_summary_id=sample_summary_id)

    url = f'{app.config["SAMPLE_URL"]}/samples/samplesummary/{sample_summary_id}'

    response = requests.delete(url=url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        if response.status_code == 404:
            logger.info(
                "Sample summary not found, could possibly have been deleted already",
                sample_summary_id=sample_summary_id,
            )
        else:
            logger.error(
                "Error uploading sample file", status=response.status_code, sample_summary_id=sample_summary_id
            )
            raise ApiError(response)

    logger.info("Successfully deleted sample", sample_summary_id=sample_summary_id)
    return


def sample_summary_state_check_required(ce_details: dict) -> bool:
    """
    Determines whether we need to check the sample summary to see if all the sample units have been loaded.
    We only need to do that in a few circumstances, generally when the collection exercise is still being created and
    when the sample summary is still in the INIT state.

    :param ce_details: A dict generated from the 'build_collection_exercise_details' function
    :return: True if we need to check and possibly modify the state of the sample summary, false otherwise.
    """
    ce_state = ce_details["collection_exercise"]["state"]
    ce_state_where_sample_summary_is_active = [
        "READY_FOR_REVIEW",
        "FAILEDVALIDATION",
        "LIVE",
        "READY_FOR_LIVE",
        "EXECUTION_STARTED",
        "VALIDATED",
        "EXECUTED",
        "ENDED",
    ]
    return ce_state not in ce_state_where_sample_summary_is_active and (
        ce_details["sample_summary"] is not None and ce_details["sample_summary"].get("state") == "INIT"
    )
