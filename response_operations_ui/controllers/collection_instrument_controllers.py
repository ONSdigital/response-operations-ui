import json
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app


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
