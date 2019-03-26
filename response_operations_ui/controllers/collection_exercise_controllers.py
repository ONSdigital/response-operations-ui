import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError
from structlog import wrap_logger
import json

from response_operations_ui.controllers.sample_controllers import get_sample_summary
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def download_report(collection_exercise_id, survey_id):
    logger.debug(
        "Downloading response chasing report",
        collection_exercise_id=collection_exercise_id,
        survey_id=survey_id,
    )

    url = (
        f"{app.config['REPORT_URL']}"
        f"/reporting-api/v1/response-chasing/download-report/"
        f"{collection_exercise_id}/{survey_id}"
    )

    response = requests.get(url)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Error retrieving collection exercise",
            collection_exercise_id=collection_exercise_id,
            survey_id=survey_id,
        )
        raise ApiError(response)

    logger.debug(
        "Successfully downloaded response chasing report",
        collection_exercise_id=collection_exercise_id,
        survey_id=survey_id,
    )
    return response


def get_collection_exercise_events_by_id(ce_id):
    logger.debug('Retrieving collection exercise events by id', collection_exercise_id=ce_id)

    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{ce_id}/events'
    response = requests.Session().get(url=url, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error("Failed to get collection exercise events", collection_exercise_id=ce_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved collection exercise events.', collection_exercise_id=ce_id)
    return response.json()


def update_event(collection_exercise_id, tag, timestamp):
    logger.debug('Updating collection exercise event date', collection_exercise_id=collection_exercise_id, tag=tag)

    formatted_timestamp = timestamp.isoformat(timespec='milliseconds')
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}/events/{tag}'
    response = requests.put(url, auth=app.config['COLLECTION_EXERCISE_AUTH'],
                            headers={'content-type': 'text/plain'}, data=formatted_timestamp)

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 400:
            logger.warning('Bad request updating event', collection_exercise_id=collection_exercise_id,
                           tag=tag, timestamp=formatted_timestamp, status=response.status_code)
            response_content = response.content.decode("utf-8")
            response_json = json.loads(response_content)
            logger.error('Validation Failed:', message=response_json['error']['message'])

            return response_json['error']['message']
        else:
            logger.error('Failed to update collection exercise event', collection_exercise_id=collection_exercise_id,
                         tag=tag, timestamp=formatted_timestamp, status=response.status_code)
        raise ApiError(response)

    logger.debug('Successfully updated event date', collection_exercise_id=collection_exercise_id,
                 tag=tag, timestamp=formatted_timestamp)
    return None


def create_collection_exercise_event(collection_exercise_id, tag, timestamp):
    logger.debug('Creating event date', collection_exercise_id=collection_exercise_id,
                 tag=tag)

    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}/events'
    formatted_timestamp = timestamp.isoformat(timespec='milliseconds')
    response = requests.Session().post(url=url, auth=app.config['COLLECTION_EXERCISE_AUTH'],
                                       json={'tag': tag, 'timestamp': formatted_timestamp})

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 400:
            logger.warning('Bad request creating event', collection_exercise_id=collection_exercise_id,
                           tag=tag, timestamp=formatted_timestamp, status=response.status_code)
            response_content = response.content.decode("utf-8")
            response_json = json.loads(response_content)
            logger.error('got error', message=response_json['error']['message'])

            return response_json['error']['message']

        logger.error("Failed to create collection exercise event",
                     collection_exercise_id=collection_exercise_id,
                     tag=tag)
        raise ApiError(response)

    logger.debug("Successfully created collection exercise event", collection_exercise_id=collection_exercise_id,
                 tag=tag)
    return None


def execute_collection_exercise(collection_exercise_id):
    logger.debug("Executing collection exercise", collection_exercise_id=collection_exercise_id)
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexerciseexecution/{collection_exercise_id}'
    response = requests.post(url, auth=app.config['COLLECTION_EXERCISE_AUTH'])
    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 404:
            logger.error('Failed to retrieve collection exercise', collection_exercise_id=collection_exercise_id)
        else:
            logger.error('Error executing collection exercise', collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug("Successfully began execution of collection exercise", collection_exercise_id=collection_exercise_id)


def update_collection_exercise_user_description(collection_exercise_id, user_description):
    logger.debug('Updating collection exercise user description',
                 collection_exercise_id=collection_exercise_id)

    header = {'Content-Type': "text/plain"}
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}/userDescription'
    response = requests.put(url, headers=header, data=user_description, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 404:
            logger.error('Error retrieving collection exercise', collection_exercise_id=collection_exercise_id)
        else:
            logger.error('Failed to update collection exercise user description',
                         collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug('Successfully updated collection exercise user description',
                 collection_exercise_id=collection_exercise_id)


def update_collection_exercise_period(collection_exercise_id, period):
    logger.debug('Updating collection exercise period', collection_exercise_id=collection_exercise_id, period=period)

    header = {'Content-Type': "text/plain"}
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}/exerciseRef'
    response = requests.put(url, headers=header, data=period, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 404:
            logger.error('Error retrieving collection exercise', collection_exercise_id=collection_exercise_id)
        else:
            logger.error('Failed to update collection exercise period', collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug('Successfully updated collection exercise period', collection_exercise_id=collection_exercise_id)


def get_collection_exercise_by_id(collection_exercise_id):
    logger.debug('Retrieving collection exercise', collection_exercise_id=collection_exercise_id)
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}'
    response = requests.get(url=url, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        log_level = logger.warning if response.status_code == 404 else logger.exception
        log_level(
            "Failed to retrieve collection exercise",
            collection_exercise_id=collection_exercise_id,
        )
        raise ApiError(response)

    logger.debug(
        "Successfully retrieved collection exercise",
        collection_exercise_id=collection_exercise_id,
    )
    return response.json()


def create_collection_exercise(survey_id, survey_name, user_description, period):
    logger.debug(
        "Creating a new collection exercise for",
        survey_id=survey_id,
        survey_name=survey_name,
    )
    header = {"Content-Type": "application/json"}
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises'

    collection_exercise_details = {
        "surveyId": survey_id,
        "name": survey_name,
        "userDescription": user_description,
        "exerciseRef": period,
    }

    response = requests.post(
        url,
        json=collection_exercise_details,
        headers=header,
        auth=app.config["COLLECTION_EXERCISE_AUTH"],
    )
    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Error creating new collection exercise", survey_id=survey_id)
        raise ApiError(response)

    logger.debug(
        "Successfully created collection exercise for",
        survey_id=survey_id,
        survey_name=survey_name,
    )


def get_collection_exercises_by_survey(survey_id):
    logger.debug("Retrieving collection exercises", survey_id=survey_id)
    url = (
        f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey/{survey_id}'
    )
    response = requests.get(url, auth=app.config["COLLECTION_EXERCISE_AUTH"])

    if response.status_code == 204:
        return []
    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception(
            "Failed to retrieve collection exercises by survey", survey_id=survey_id
        )
        raise ApiError(response)

    logger.debug(
        "Successfully retrieved collection exercises by survey", survey_id=survey_id
    )
    return response.json()


def get_case_group_status_by_collection_exercise(case_groups, collection_exercise_id):
    return next(
        case_group["caseGroupStatus"]
        for case_group in case_groups
        if case_group["collectionExerciseId"] == collection_exercise_id
    )


def unlink_sample_summary(collection_exercise_id, sample_summary_id):
    logger.debug(
        "un-linking sample summary from collection exercise",
        collection_exercise_id=collection_exercise_id,
        sample_summary_id=sample_summary_id,
    )

    url = (
        f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/unlink/'
        f"{collection_exercise_id}/sample/{sample_summary_id}"
    )

    response = requests.delete(url, auth=app.config["COLLECTION_EXERCISE_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception(
            "Failed to unlink sample summary from collection exercise",
            collection_exercise_id=collection_exercise_id,
            sample_summary_id=sample_summary_id,
        )
        return False

    logger.debug(
        "Successfully unlinked sample summary from a collection exercise",
        collection_exercise_id=collection_exercise_id,
        sample_summary_id=sample_summary_id,
    )
    return True


def get_collection_exercise_from_list(exercises, period):
    return next(
        (exercise for exercise in exercises if exercise["exerciseRef"] == period), None
    )


def get_linked_sample_summary_id(collection_exercise_id):
    logger.debug('Retrieving sample linked to collection exercise', collection_exercise_id=collection_exercise_id)
    url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/link/{collection_exercise_id}'
    response = requests.get(url, auth=app.config['COLLECTION_EXERCISE_AUTH'])

    if response.status_code == 204:
        logger.info('No samples linked to collection exercise', collection_exercise_id=collection_exercise_id)
        return
    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error retrieving sample summaries linked to collection exercise',
                     collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    # currently, we only want a single sample summary
    sample_summary_id = response.json()[0]

    logger.debug('Successfully retrieved linked sample summary',
                 collection_exercise_id=collection_exercise_id,
                 sample_summary_id=sample_summary_id)
    return sample_summary_id


def link_sample_summary_to_collection_exercise(collection_exercise_id, sample_summary_id):
    logger.debug(
        "Linking sample summary to collection exercise",
        collection_exercise_id=collection_exercise_id,
        sample_summary_id=sample_summary_id,
    )
    url = (
        f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/link/{collection_exercise_id}'
    )
    # Currently we only need to link a single sample to a single collection exercise
    payload = {"sampleSummaryIds": [str(sample_summary_id)]}
    response = requests.put(
        url, auth=app.config["COLLECTION_EXERCISE_AUTH"], json=payload
    )

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Error retrieving collection exercise",
            collection_exercise_id=collection_exercise_id,
            sample_summary_id=sample_summary_id,
        )
        raise ApiError(response)

    logger.debug(
        "Successfully linked sample summary with collection exercise",
        collection_exercise_id=collection_exercise_id,
        sample_summary_id=sample_summary_id,
    )
    return response.json()


def get_collection_exercises_with_events_and_samples_by_survey_id(survey_id):
    logger.debug(
        "Retrieving collection exercise with events and samples",
        survey_id=survey_id
    )

    ce_list = get_collection_exercises_by_survey(survey_id)

    for ce in ce_list:
        ce['events'] = get_collection_exercise_events_by_id(ce['id'])
        sample_summary_id = get_linked_sample_summary_id(ce['id'])
        if sample_summary_id:
            ce['sample_summary'] = get_sample_summary(sample_summary_id)

    logger.debug('Successfully retrieved collection exercise details', survey_id=survey_id)

    return ce_list
