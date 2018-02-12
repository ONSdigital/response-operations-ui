import logging
import jwt
import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def send_message(message_json):
    logger.debug("Sending messsage")

    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message'
    # This will be removed once UAA is completed.  For now we need the call to backstage to include
    # an Authorization in its header a JWT that includes party_id and role.
    encoded_jwt = jwt.encode({'user': 'BRES', 'party_id': 'BRES', 'role': 'internal'}, 'testsecret', algorithm='HS256')

    response = requests.post(url, headers={'Authorization': encoded_jwt, 'Content-Type': 'application/json',
                                           'Accept': 'application/json'}, data=message_json)
    if response.status_code != 201:
        raise ApiError(response)
