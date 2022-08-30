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


def check_if_all_sample_units_present_and_change_state(sample_summary_id):
    """
    Calls endpoint in sample that counts if expected sample units == actual number of sample units
    and changes sample summary state to ACTIVE if the two number do match.

    :param sample_summary_id:
    :return:
    """
    logger.info("Retrieving sample summary", sample_summary_id=sample_summary_id)
    url = f'{app.config["SAMPLE_URL"]}/samples/samplesummary/{sample_summary_id}/check-all-units-present'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Error checking sample summary", sample_summary_id=sample_summary_id, status_code=response.status_code
        )
        raise ApiError(response)

    response_json = response.json()
    logger.info("Successfully checked if all units present", response=response_json)
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
