import json
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def upload_collection_instrument(collection_exercise_id, file, form_type=None):
    logger.debug('Uploading collection instrument', collection_exercise_id=collection_exercise_id, form_type=form_type)
    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}' \
          f'/collection-instrument-api/1.0.2/upload/{collection_exercise_id}'

    params = dict()

    if form_type:
        classifiers = {
            "form_type": form_type,
        }
        params['classifiers'] = json.dumps(classifiers)

    files = {"file": (file.filename, file.stream, file.mimetype)}
    response = requests.post(url, files=files, params=params, auth=app.config['COLLECTION_INSTRUMENT_AUTH'])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception('Failed to upload collection instrument', collection_exercise_id=collection_exercise_id,
                         form_type=form_type, status=response.status_code)
        return False

    logger.debug('Successfully uploaded collection instrument', collection_exercise_id=collection_exercise_id,
                 form_type=form_type)
    return True


def link_collection_instrument(ce_id, ci_id):
    logger.debug('Linking collection instrument to collection exercise',
                 collection_exercise_id=ce_id, collection_instrument_id=ci_id)
    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}' \
          f'/collection-instrument-api/1.0.2/link-exercise/{ci_id}/{ce_id}'

    response = requests.post(url, auth=app.config['COLLECTION_INSTRUMENT_AUTH'])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to link collection instrument to collection exercise',
                     collection_exercise_id=ce_id, collection_instrument_id=ci_id, status=response.status_code)
        return False

    logger.debug('Successfully linked collection instrument to collection exercise',
                 collection_exercise_id=ce_id, collection_instrument_id=ci_id)
    return True


def unlink_collection_instrument(ce_id, ci_id):
    logger.debug('Unlinking collection instrument and collection exercise',
                 collection_exercise_id=ce_id, collection_instrument_id=ci_id)
    url = f'{app.config["COLLECTION_INSTRUMENT_URL"]}' \
          f'/collection-instrument-api/1.0.2/unlink-exercise/{ci_id}/{ce_id}'

    response = requests.put(url, auth=app.config['COLLECTION_INSTRUMENT_AUTH'])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to unlink collection instrument and collection exercise',
                     collection_exercise_id=ce_id, collection_instrument_id=ci_id, status=response.status_code)
        return False

    logger.debug('Successfully unlinked collection instrument and collection exercise',
                 collection_exercise_id=ce_id, collection_instrument_id=ci_id)
    return True


def get_collection_instruments_by_classifier(survey_id=None, collection_exercise_id=None, ci_type=None):
    logger.debug('Retrieving collection instruments', survey_id=survey_id,
                 collection_exercise_id=collection_exercise_id, ci_type=ci_type)
    url = (
        f'{app.config["COLLECTION_INSTRUMENT_URL"]}'
        f'/collection-instrument-api/1.0.2/collectioninstrument'
    )

    classifiers = _build_classifiers(collection_exercise_id, survey_id, ci_type)
    response = requests.get(url, auth=app.config['COLLECTION_INSTRUMENT_AUTH'],
                            params={'searchString': json.dumps(classifiers)})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Error retrieving collection instruments')
        raise ApiError(response)

    logger.debug('Successfully retrieved collection instruments', survey_id=survey_id,
                 collection_exercise_id=collection_exercise_id, ci_type=ci_type)
    return response.json()


def _build_classifiers(collection_exercise_id=None, survey_id=None, ci_type=None):
    classifiers = {}
    if survey_id:
        classifiers['SURVEY_ID'] = survey_id
    if collection_exercise_id:
        classifiers['COLLECTION_EXERCISE'] = collection_exercise_id
    if ci_type:
        classifiers['TYPE'] = ci_type
    return classifiers
