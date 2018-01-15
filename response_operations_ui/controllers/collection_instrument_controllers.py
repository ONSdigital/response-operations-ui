import json
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def upload_collection_instrument(short_name, period, file):
    logger.debug('Uploading collection instrument', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/collection-instrument/{short_name}/{period}'
    response = requests.post(url, files={"file": (file.filename, file.stream, file.mimetype)})
    if response.status_code != 201:
        raise ApiError(response)


def get_collection_instruments(short_name, period):
    logger.debug('Getting collection instruments', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/collection-instrument/{short_name}/{period}'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)
    return json.loads(response.text)
