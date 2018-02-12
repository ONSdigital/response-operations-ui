import logging

import jwt
import requests
from flask import current_app
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_message_list(params):
    logger.debug("Retrieving Message list")

    url = f'{current_app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
    # This will be removed once UAA is completed.  For now we need the call to backstage to include
    # an Authorization in its header a JWT that includes party_id and role.
    encoded_jwt = jwt.encode({'party_id': 'BRES', 'role': 'internal'}, 'testsecret', algorithm='HS256')
    response = requests.get(url, headers={'Authorization': encoded_jwt}, params=params)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Message retrieval failed")
        raise ApiError(response)

    logger.debug("Retrieval successful")
    try:
        messages = response.json()['messages']
        return messages
    except KeyError:
        # TODO: Look to fail more gracefully.  Returning an empty list will display
        # 'you have no mail' on the screen, which isn't accurate as it's more accurately
        # 'we don't know if you have messages, try again later'.  This should error for the
        # user but not give a server error page.
        logger.exception("Response was successful but didn't contain messages element")
        return []
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
