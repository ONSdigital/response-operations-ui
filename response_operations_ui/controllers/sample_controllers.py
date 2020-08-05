import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def get_sample_summary(sample_summary_id):
    logger.info('Retrieving sample summary', sample_summary_id=sample_summary_id)
    url = f'{app.config["SAMPLE_URL"]}/samples/samplesummary/{sample_summary_id}'

    response = requests.get(url, auth=app.config['BASIC_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error retrieving sample summary',
                     sample_summary_id=sample_summary_id,
                     status_code=response.status_code)
        raise ApiError(response)

    logger.info('Successfully retrieved sample summary', sample_summary_id=sample_summary_id)
    return response.json()


def upload_sample(short_name, period, file):
    logger.info('Uploading sample', short_name=short_name, period=period, filename=file.filename)

    if app.config["SAMPLE_FILE_UPLOADER_URL_ENABLED"]:
        url = f'{app.config["SAMPLE_FILE_UPLOADER_URL"]}/samples/fileupload'
    else:
        url = f'{app.config["SAMPLE_URL"]}/samples/B/fileupload'

    response = requests.post(url=url, auth=app.config['BASIC_AUTH'], files={'file': file})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error uploading sample file', status=response.status_code)
        raise ApiError(response)

    sample_summary = response.json()

    logger.info('Successfully uploaded sample file',
                response_json=sample_summary,
                sample_id=sample_summary['id'])

    return sample_summary
