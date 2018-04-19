import json
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app


logger = wrap_logger(logging.getLogger(__name__))


def upload_collection_instrument(short_name, period, file, form_type=None):
    logger.debug('Uploading collection instrument', short_name=short_name, period=period, form_type=form_type)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/{short_name}/{period}'

    params = dict()

    if form_type:
        classifiers = {
            "form_type": form_type,
        }
        params['classifiers'] = json.dumps(classifiers)

    response = requests.post(url, files={"file": (file.filename, file.stream, file.mimetype)}, params=params)
    if response.status_code != 201:
        logger.error('Failed to upload collection instrument', short_name=short_name, period=period,
                     form_type=form_type, status=response.status_code)
        return False

    logger.debug('Successfully uploaded collection instrument', short_name=short_name, period=period,
                 form_type=form_type)
    return True


def link_collection_instrument(ce_id, ci_id):
    logger.debug('Linking collection instrument to collection exercise', ce_id=ce_id, ci_id=ci_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/link/{ci_id}/{ce_id}'
    response = requests.post(url)
    if response.status_code != 200:
        logger.error('Failed to link collection instrument to collection exercise', ce_id=ce_id, ci_id=ci_id,
                     status=response.status_code)
        return False

    logger.debug('Successfully linked collection instrument to collection exercise', ce_id=ce_id, ci_id=ci_id)
    return True


def unlink_collection_instrument(ce_id, ci_id):
    logger.debug('Unlinking collection instrument and collection exercise', ce_id=ce_id, ci_id=ci_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/unlink/{ci_id}/{ce_id}'
    response = requests.put(url)
    if response.status_code != 200:
        logger.error('Failed to unlink collection instrument and collection exercise', ce_id=ce_id, ci_id=ci_id,
                     status=response.status_code)
        return False

    logger.debug('Successfully unlinked collection instrument and collection exercise', ce_id=ce_id, ci_id=ci_id)
    return True
