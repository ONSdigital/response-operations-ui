import logging

import requests
from flask import jsonify, make_response
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def upload_sample(short_name, period, file, exercise):
    logger.debug('Uploading sample', short_name=short_name, period=period, filename=file.filename)

    if not exercise:
        return make_response(jsonify({'message': 'Collection exercise not found'}), 404)

    survey_type = 'B'
    url = f'{app.config["SAMPLE_URL"]}/samples/{survey_type}/fileupload'
    response = requests.post(url=url, auth=app.config['SAMPLE_AUTH'], files={'file': file})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error uploading sample file',
                  collection_exercise_id=exercise['id'], status=response.status_code, survey_type=survey_type)
        raise ApiError(response)

    sample_summary = response.json()

    logger.debug('Successfully uploaded sample file',
                 collection_exercise_id=exercise['id'],
                 response_json=sample_summary,
                 survey_type=survey_type)

    logger.info('Successfully uploaded sample', sample_id=sample_summary['id'])

    return sample_summary
