import logging

import requests

from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def get_sample_summary(sample_summary_id):
    logger.debug('Retrieving sample summary', sample_summary_id=sample_summary_id)
    url = f'{app.config["SAMPLE_URL"]}/samples/samplesummary/{sample_summary_id}'

    response = requests.get(url, auth=app.config['SAMPLE_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error retrieving sample summary',
                     sample_summary_id=sample_summary_id,
                     status_code=response.status_code)
        raise ApiError(response)

    logger.debug('Successfully retrieved sample summary', sample_summary_id=sample_summary_id)
    return response.json()


def upload_sample(short_name, period, file):
    logger.debug('Uploading sample', short_name=short_name, period=period, filename=file.filename)

    survey_type = 'B'
    url = f'{app.config["SAMPLE_URL"]}/samples/{survey_type}/fileupload'
    response = requests.post(url=url, auth=app.config['SAMPLE_AUTH'], files={'file': file})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error uploading sample file', status=response.status_code, survey_type=survey_type)
        raise ApiError(response)

    sample_summary = response.json()

    logger.debug('Successfully uploaded sample file',
                 response_json=sample_summary,
                 survey_type=survey_type,
                 sample_id=sample_summary['id'])

    return sample_summary


def search_samples_by_postcode(postcode) -> dict:
    logger.debug("Searching for samples by postcode")

    url = f'{app.config["SAMPLE_URL"]}/samples/sampleunits'
    response = requests.get(url=url,
                            auth=app.config['SAMPLE_AUTH'],
                            params={'postcode': postcode})

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 404:
            logger.debug("No samples were found for postcode")
            return dict()
        logger.exception('Error searching for sample by postcode', status=response.status_code)
        raise ApiError(response)

    return response.json()
