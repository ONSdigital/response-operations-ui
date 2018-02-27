import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app


logger = wrap_logger(logging.getLogger(__name__))


def upload_collection_instrument(short_name, period, file):
    logger.debug('Uploading collection instrument', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/{short_name}/{period}'
    response = requests.post(url, files={"file": (file.filename, file.stream, file.mimetype)})
    if response.status_code != 201:
        logger.error('Failed to upload collection instrument', short_name=short_name, period=period,
                     status=response.status_code)
        return False

    logger.debug('Successfully uploaded collection instrument', short_name=short_name, period=period)
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
