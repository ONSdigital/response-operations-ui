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
        logger.error('Failed to upload collection instrument', short_name=short_name, period=period)
        return False

    logger.debug('Successfully uploaded collection instrument', short_name=short_name, period=period)
    return True
