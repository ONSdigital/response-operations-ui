import json
import logging

import requests
from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def upload_collection_instrument(collection_exercise_id, file, form_type=None):
    """
    Uploads a standard SEFT collection instrument.  This will be linked to the collection exercise via the id provided.

    :param collection_exercise_id: The collection exercise this instrument will be linked to
    :type collection_exercise_id: str
    :param file: The collection instrument (spreadsheet) to be uploaded
    :param form_type: A formtype to act as metadata for the instrument
    :return: True on success, False on failure.
    """
    logger.info("Uploading collection instrument", collection_exercise_id=collection_exercise_id, form_type=form_type)
    url = (
        f'{app.config["COLLECTION_INSTRUMENT_URL"]}' f"/collection-instrument-api/1.0.2/upload/{collection_exercise_id}"
    )

    params = dict()

    if form_type:
        classifiers = {
            "form_type": form_type,
        }
        params["classifiers"] = json.dumps(classifiers)

    files = {"file": (file.filename, file.stream, file.mimetype)}
    response = requests.post(url, files=files, params=params, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception(
            "Failed to upload collection instrument",
            collection_exercise_id=collection_exercise_id,
            form_type=form_type,
            status=response.status_code,
        )
        if response.headers["Content-Type"] == "application/json":
            return False, response.json().get("errors")[0]
        return False, None

    logger.info(
        "Successfully uploaded collection instrument",
        collection_exercise_id=collection_exercise_id,
        form_type=form_type,
    )
    return True, None


def upload_ru_specific_collection_instrument(collection_exercise_id, file, ru_ref):
    """
    Uploads an reporting unit specific collection instrument. This is different to a standard SEFT as we supply an
    ru_ref to link the instrument to both a reporting unit AND a collection exercise where a standard SEFT is linked
    ONLY to a collection exercise.  An example of a survey that uses ru specific collection instruments is BRES.

    :param collection_exercise_id: The collection exercise this instrument will be linked to
    :type collection_exercise_id: str
    :param file: The collection instrument (spreadsheet) to be uploaded
    :param ru_ref: The ru_ref to link the collection instrument to.
    :type ru_ref: str
    :return: True, None on success. False, error text on failure (if the response is in json format) and False, None
             otherwise.
    :rtype: tuple
    """
    bound_logger = logger.bind(collection_exercise_id=collection_exercise_id, ru_ref=ru_ref)
    bound_logger.info("Uploading BRES collection instrument")
    url = (
        f'{app.config["COLLECTION_INSTRUMENT_URL"]}'
        f"/collection-instrument-api/1.0.2/upload/{collection_exercise_id}/{ru_ref}"
    )

    files = {"file": (file.filename, file.stream, file.mimetype)}
    response = requests.post(url, files=files, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bound_logger.error("Failed to upload BRES collection instrument", status=response.status_code, exc_info=True)
        if response.headers["Content-Type"] == "application/json":
            return False, response.json().get("errors")[0]
        return False, None

    bound_logger.info("Successfully uploaded BRES collection instrument")
    return True, None


def link_collection_instrument_to_survey(survey_uuid, eq_id, form_type):
    """This links an eq_id and form_type to a survey so they can be used by a collection exercise.  This only relates to
    EQ surveys.  These values map to filenames of schemas in EQ.  An example of this would be stocks_0001.json.  The
    eq_id here would be 'stocks',  the form_type would be '0001' and the survey_uuid would match the stocks survey in
    the survey service.

    :param survey_uuid: A uuid of a survey
    :type survey_uuid: str
    :param eq_id: The first part of an eq filename, typically the name of the survey
    :type eq_id: str
    :param form_type: The formtype of the collection instrument and the second part of the eq filename
    :type form_type: str
    """
    logger.info("Linking collection instrument to survey", survey_uuid=survey_uuid, eq_id=eq_id, form_type=form_type)
    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}/collection-instrument-api/1.0.2/upload'
    payload = {
        "survey_id": survey_uuid,
        "classifiers": f'{{"form_type":"{form_type}","eq_id":"{eq_id}"}}',
    }
    response = requests.post(url, params=payload, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error(
            "Failed to link collection instrument to survey",
            survey_uuid=survey_uuid,
            eq_id=eq_id,
            form_type=form_type,
            status=response.status_code,
            exc_info=True,
        )
        raise ApiError(response)

    logger.info(
        "Successfully linked collection instrument to survey", survey_uuid=survey_uuid, eq_id=eq_id, form_type=form_type
    )


def link_collection_instrument(ce_id, ci_id):
    """Links a collection instrument to a collection exercise

    :param ce_id: A uuid of a collection exercise
    :type ce_id: str
    :param ci_id: A uuid of a collection instrument
    :type ci_id: str
    :return: True on success.  False on failure
    :rtype: bool
    """
    bound_logger = logger.bind(collection_exercise_id=ce_id, collection_instrument_id=ci_id)
    bound_logger.info("Linking collection instrument to collection exercise")
    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}' f"/collection-instrument-api/1.0.2/link-exercise/{ci_id}/{ce_id}"

    response = requests.post(url, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bound_logger.error("Failed to link collection instrument to collection exercise", status=response.status_code)
        return False

    bound_logger.info("Successfully linked collection instrument to collection exercise")
    return True


def unlink_collection_instrument(ce_id, ci_id):
    """Unlinks a collection instrument from a collection exercise

    :param ce_id: A uuid of a collection exercise
    :type ce_id: str
    :param ci_id: A uuid of a collection instrument
    :type ci_id: str
    :return: True on success.  False on failure
    :rtype: bool
    """
    bound_logger = logger.bind(collection_exercise_id=ce_id, collection_instrument_id=ci_id)
    bound_logger.info("Unlinking collection instrument and collection exercise")
    url = (
        f'{app.config["COLLECTION_INSTRUMENT_URL"]}' f"/collection-instrument-api/1.0.2/unlink-exercise/{ci_id}/{ce_id}"
    )

    response = requests.put(url, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bound_logger.error(
            "Failed to unlink collection instrument and collection exercise", status=response.status_code
        )
        return False

    bound_logger.info("Successfully unlinked collection instrument and collection exercise")
    return True


def delete_seft_collection_instrument(ci_id: str) -> bool:
    """Deletes a SEFT collection instrument

    :param ci_id: A uuid of a collection instrument
    :rtype: bool
    """
    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}/collection-instrument-api/1.0.2/delete/{ci_id}'
    response = requests.delete(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error(response.text, status=response.status_code)
        return False

    return True


def get_collection_instruments_by_classifier(survey_id=None, collection_exercise_id=None, ci_type=None):
    logger.info(
        "Retrieving collection instruments",
        survey_id=survey_id,
        collection_exercise_id=collection_exercise_id,
        ci_type=ci_type,
    )

    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}/collection-instrument-api/1.0.2/collectioninstrument'
    classifiers = _build_classifiers(collection_exercise_id, survey_id, ci_type)
    response = requests.get(url, auth=app.config["BASIC_AUTH"], params={"searchString": json.dumps(classifiers)})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error("Error retrieving collection instruments")
        raise ApiError(response)

    logger.info(
        "Successfully retrieved collection instruments",
        survey_id=survey_id,
        collection_exercise_id=collection_exercise_id,
        ci_type=ci_type,
    )
    return response.json()


def _build_classifiers(collection_exercise_id=None, survey_id=None, ci_type=None):
    classifiers = {}
    if survey_id:
        classifiers["SURVEY_ID"] = survey_id
    if collection_exercise_id:
        classifiers["COLLECTION_EXERCISE"] = collection_exercise_id
    if ci_type:
        classifiers["TYPE"] = ci_type
    return classifiers
