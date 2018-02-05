import logging
import jwt
import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_message_list():

    logger.debug("Retrieving Message list")
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
    encoded_jwt = jwt.encode({'party_id': 'BRES', 'role': 'internal'}, 'testsecret', algorithm='HS256')

    response = requests.get(url, headers={'Authorization': encoded_jwt})
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug("Retrieve success")

    return response.json()
