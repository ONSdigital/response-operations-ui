import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def upload_sample(short_name, period, file):
    logger.debug('Uploading sample', short_name=short_name, period=period, filename=file.filename)
    url = f'{app.config["BACKSTAGE_BASE_URL"]}/v1/sample/{short_name}/{period}'
    response = requests.post(url, files={"file": (file.filename, file.stream, file.mimetype)})
    if response.status_code != 201:
        raise ApiError(response)

    logger.debug('Successfully uploaded sample')
