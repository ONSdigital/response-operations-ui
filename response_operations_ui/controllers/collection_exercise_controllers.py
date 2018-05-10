import logging

import requests
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.common.mappers import map_ce_response_status, map_region
from response_operations_ui.controllers import case_controller, party_controller
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


def get_collection_exercise_by_id(collection_exercise_id):
    logger.debug('Retrieving collection exercise', collection_exercise_id=collection_exercise_id)
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}'
    response = requests.get(url, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code == 404 else logger.exception
        log_level('Failed to retrieve collection exercise', collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved collection exercise', collection_exercise_id=collection_exercise_id)
    return response.json()


def create_collection_exercise(survey_id, survey_name, user_description, period):
    logger.debug('Creating a new collection exercise for', survey_id=survey_id, survey_name=survey_name)
    header = {'Content-Type': "application/json"}
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises'

    collection_exercise_details = {
        "surveyId": survey_id,
        "name": survey_name,
        "userDescription": user_description,
        "exerciseRef": period
    }

    response = requests.post(url, json=collection_exercise_details, headers=header,
                             auth=app.config['COLLECTION_EXERCISE_AUTH'])
    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception('Error creating new collection exercise', survey_id=survey_id)
        return ApiError(response)

    logger.debug('Successfully created collection exercise for', survey_id=survey_id, survey_name=survey_name)


def get_collection_exercises_by_survey(survey_id):
    logger.debug('Retrieving collection exercises', survey_id=survey_id)
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey/{survey_id}'

    response = requests.get(url, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception('Failed to retrieve collection exercises by survey', survey_id=survey_id)
        return ApiError(response)

    logger.debug('Successfully retrieved collection exercises by survey', survey_id=survey_id)
    return response.json()


def add_collection_exercise_details(collection_exercise, reporting_unit, case_groups):
    response_status = get_case_group_status_by_collection_exercise(case_groups, collection_exercise['id'])
    reporting_unit_ce = party_controller.get_business_party_by_party_id(reporting_unit['id'], collection_exercise['id'])
    statuses = case_controller.get_available_case_group_statuses_direct(collection_exercise['id'],
                                                                        reporting_unit['sampleUnitRef'])
    ce_extra = {
        **collection_exercise,
        'responseStatus': map_ce_response_status(response_status),
        'companyName': reporting_unit_ce['name'],
        'companyRegion': map_region(reporting_unit_ce['region']),
        'trading_as': reporting_unit_ce['trading_as'],
        'statuses': statuses.values()
    }
    return ce_extra


def get_case_group_status_by_collection_exercise(case_groups, collection_exercise_id):
    for case_group in case_groups:
        if case_group['collectionExerciseId'] == collection_exercise_id:
            return case_group['caseGroupStatus']
