import logging

import requests
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def download_report(collection_exercise_id, survey_id):
    logger.debug(
        "Downloading response chasing report",
        collection_exercise_id=collection_exercise_id,
        survey_id=survey_id,
    )

    url = (
        app.config["RM_REPORT_SERVICE"]
        "reporting-api/v1/response-chasing/download-report/"
        f"{collection_exercise_id}/{survey_id}"
    )

    response = requests.get(url)

    if response.status_code != 200:
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


def get_collection_exercise(short_name, period):
    logger.debug(
        "Retrieving collection exercise details", short_name=short_name, period=period
    )
    url = (
        f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}'
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug(
        "Successfully retrieved collection exercise details",
        short_name=short_name,
        period=period,
    )
    return response.json()


def get_collection_exercise_event_page_info(short_name, period):
    logger.debug(
        "Retrieving collection exercise details for the event page",
        short_name=short_name,
        period=period,
    )
    url = (
        f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/events'
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug(
        "Successfully retrieved collection exercise details for the event page",
        short_name=short_name,
        period=period,
    )
    return response.json()


def update_event(short_name, period, tag, timestamp):
    logger.debug("Updating event date", short_name=short_name, period=period, tag=tag)
    url = (
        f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/events/{tag}'
    )
    formatted_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:00.000+0000")
    response = requests.put(url, json={"timestamp": formatted_timestamp})

    if response.status_code == 400:
        logger.warning(
            "Bad request updating event",
            short_name=short_name,
            period=period,
            tag=tag,
            timestamp=timestamp,
            status=response.status_code,
        )
        return False
    elif response.status_code != 201:
        raise ApiError(response)

    logger.debug(
        "Successfully updated event date", short_name=short_name, period=period, tag=tag
    )
    return True


def execute_collection_exercise(short_name, period):
    logger.debug("Executing collection exercise", short_name=short_name, period=period)
    url = (
        f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}/execute'
    )
    response = requests.post(url)
    if response.ok:
        logger.debug(
            "Successfully began execution of collection exercise",
            short_name=short_name,
            period=period,
        )
        return True

    logger.debug(
        "Failed to execute collection exercise", short_name=short_name, period=period
    )


def update_collection_exercise_details(
    collection_exercise_id, user_description, period
):
    logger.debug(
        "Updating collection exercise details",
        collection_exercise_id=collection_exercise_id,
    )
    url = (
        f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/'
        f"update-collection-exercise-details/{collection_exercise_id}"
    )

    collection_exercise_details = {
        "user_description": user_description,
        "period": period,
    }

    response = requests.put(url, json=collection_exercise_details)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug(
        "Successfully updated collection exercise details",
        collection_exercise_id=collection_exercise_id,
    )


def get_collection_exercise_by_id(collection_exercise_id):
    logger.debug(
        "Retrieving collection exercise", collection_exercise_id=collection_exercise_id
    )
    url = (
        f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}'
    )
    response = requests.get(url, auth=app.config["COLLECTION_EXERCISE_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
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
        return ApiError(response)

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


def link_sample_summary_to_collection_exercise(
    collection_exercise_id, sample_summary_id
):
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
