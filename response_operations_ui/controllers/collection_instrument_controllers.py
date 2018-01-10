import json
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def upload_collection_instrument(short_name, period, file):
    logger.debug('Retrieving collection exercise details', short_name=short_name, period=period)
    url = f'{app.config["BACKSTAGE_API_URL"]}/collection-instrument/{short_name}/{period}'
    response = requests.post(url, file={'file': file})
    if response.status_code != 200:
        raise ApiError(response)

