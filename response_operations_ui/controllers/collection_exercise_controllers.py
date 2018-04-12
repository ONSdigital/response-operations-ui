import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def download_report(collection_exercise_id):
    logger.debug('Downloading response chasing report', collection_exercise_id=collection_exercise_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/download-report/{collection_exercise_id}'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)
    logger.debug('Successfully downloaded response chasing report', collection_exercise_id=collection_exercise_id)
    return response


def get_collection_exercise(short_name, period):
    logger.debug('Retrieving collection exercise details', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved collection exercise details',
                 short_name=short_name, period=period)
    return response.json()


def execute_collection_exercise(short_name, period):
    logger.debug('Executing collection exercise', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/execute'
    response = requests.post(url)
    if response.ok:
        logger.debug('Successfully began execution of collection exercise',
                     short_name=short_name, period=period)
        return True


def update_collection_exercise_details(collection_exercise_id, user_description, period):
    logger.debug('Updating collection exercise details', collection_exercise_id=collection_exercise_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/update-collection-exercise-details/' \
          f'{collection_exercise_id}'

    collection_exercise_details = {
        "user_description": user_description,
        "period": period
    }

    response = requests.put(url, json=collection_exercise_details)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully updated collection exercise details', collection_exercise_id=collection_exercise_id)
