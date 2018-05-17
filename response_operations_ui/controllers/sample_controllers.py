import logging

import requests

from flask import jsonify, make_response, request

from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.common.filters import get_collection_exercise_by_period

logger = wrap_logger(logging.getLogger(__name__))


def upload_sample(short_name, period, file):
    logger.debug('Uploading sample', short_name=short_name, period=period, filename=file.filename)

    survey = survey_controllers.get_survey_by_shortname(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
    # Find the collection exercise for the given period
    exercise = get_collection_exercise_by_period(exercises, period)
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
                     collection_exercise_id=exercise['id'],
                     status=response.status_code,
                     survey_type=survey_type)
        raise ApiError(response)

    sample_summary = response.json()

    logger.debug('Successfully uploaded sample file',
                 collection_exercise_id=exercise['id'],
                 response_json=sample_summary,
                 survey_type=survey_type)

    logger.info('Successfully uploaded sample', sample_id=sample_summary['id'])

    logger.info('Linking sample summary with collection exercise',
                collection_exercise_id=exercise['id'],
                sample_id=sample_summary['id'])

    collection_exercise_controllers.link_sample_summary_to_collection_exercise(
        collection_exercise_id=exercise['id'],
        sample_summary_id=sample_summary['id'])

    logger.info('Successfully linked sample to collection exercise',
                collection_exercise_id=exercise['id'],
                sample_id=sample_summary['id'])

    return sample_summary
