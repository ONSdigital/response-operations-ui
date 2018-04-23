import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def download_report(collection_exercise_id, survey_id):
    logger.debug('Downloading response chasing report',
                 collection_exercise_id=collection_exercise_id, survey_id=survey_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise' \
          f'/download-report/{collection_exercise_id}/{survey_id}'

    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully downloaded response chasing report',
                 collection_exercise_id=collection_exercise_id, survey_id=survey_id)
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


def get_collection_exercise_event_page_info(short_name, period):
    logger.debug('Retrieving collection exercise details for the event page',
                 short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/events'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved collection exercise details for the event page',
                 short_name=short_name, period=period)
    return response.json()


def update_event(short_name, period, tag, timestamp):
    logger.debug('Updating event date',
                 short_name=short_name, period=period, tag=tag)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/events/{tag}'
    formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:00.000+0000')
    response = requests.put(url, json={'timestamp': formatted_timestamp})

    if response.status_code == 400:
        logger.warning('Bad request updating event',
                       short_name=short_name, period=period, tag=tag, timestamp=timestamp, status=response.status_code)
        return False
    elif response.status_code != 201:
        raise ApiError(response)

    logger.debug('Successfully updated event date',
                 short_name=short_name, period=period, tag=tag)
    return True


def execute_collection_exercise(short_name, period):
    logger.debug('Executing collection exercise', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/execute'
    response = requests.post(url)
    if response.ok:
        logger.debug('Successfully began execution of collection exercise',
                     short_name=short_name, period=period)
        return True

    logger.debug('Failed to execute collection exercise', short_name=short_name, period=period)


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
