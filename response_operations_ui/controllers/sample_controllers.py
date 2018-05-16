import logging

import requests
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))

def upload_sample(collection_exercise_id, sample_file, survey_type='B'):
    logger.debug('Uploading sample file',
                 collection_exercise_id=collection_exercise_id,
                 survey_type=survey_type)
    url = f'{app.config["SAMPLE_URL"]}/samples/{survey_type}/fileupload'
    response = requests.post(url=url, auth=app.config['SAMPLE_AUTH'], files={'file': sample_file})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error uploading sample file',
                     collection_exercise_id=collection_exercise_id,
                     status=response.status_code,
                     survey_type=survey_type)
        raise ApiError(response)

    response_json = response.json()

    logger.debug('Successfully uploaded sample file',
                 collection_exercise_id=collection_exercise_id,
                 response_json=response_json,
                 survey_type=survey_type)
    return response_json