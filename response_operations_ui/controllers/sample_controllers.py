import json
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def upload_sample(ce, file):
    logger.debug('Uploading sample', collection_exercise=ce, filename=file.filename)
    url = f'{app.config["BACKSTAGE_API_URL"]}/sample'
    params = {'collection_exercise_id': ce}
    response = requests.post(url, params=params, files={"file": (file.filename, file.stream, file.mimetype)})
    if response.status_code != 201:
        raise ApiError(response)

    logger.debug('Successfully uploaded sample', collection_exercise=ce, filename=file.filename)

    return json.loads(response.text)
