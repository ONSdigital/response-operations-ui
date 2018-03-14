import logging

import requests
from flask import current_app, session
from flask_login import current_user
from requests.exceptions import HTTPError, RequestException
from json import JSONDecodeError
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError, NoMessagesError, InternalError

logger = wrap_logger(logging.getLogger(__name__))


def get_conversation(thread_id):
    logger.debug("Retrieving thread")

    url = f'{current_app.config["BACKSTAGE_API_URL"]}/v1/secure-message/threads/{thread_id}'

    response = requests.get(url, headers={'Authorization': _get_jwt()})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        logger.exception("Thread retrieval failed", thread_id=thread_id)
        raise ApiError(response)
    logger.debug("Thread retrieval successful")

    try:
        return response.json()
    except JSONDecodeError:
        logger.exception("the response could not be decoded")
        raise ApiError(response)


def get_thread_list(params):
    logger.debug("Retrieving threads list")

    url = f'{current_app.config["BACKSTAGE_API_URL"]}/v1/secure-message/threads'
    # This will be removed once UAA is completed.  For now we need the call to backstage to include
    # an Authorization in its header a JWT that includes party_id and role.

    response = requests.get(url, headers={'Authorization': _get_jwt()}, params=params)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Threads retrieval failed")
        raise ApiError(response)

    logger.debug("Retrieval successful")
    try:
        messages = response.json()['messages']
        return messages
    except KeyError:
        logger.exception("Response was successful but didn't contain a 'messages' key")
        raise NoMessagesError


def send_message(message_json):
    try:
        response = _post_new_message(message_json).raise_for_status()
        logger.info("new message has been sent with response ", response=response)
    except KeyError as ex:
        logger.exception("Message sending failed due to internal error")
        raise InternalError(ex)
    except HTTPError as ex:
        logger.exception("Message sending failed due to API Error")
        raise ApiError(ex.response)


def _post_new_message(message):
    return requests.post(_get_url(), headers={'Authorization': _get_jwt(), 'Content-Type': 'application/json',
                                              'Accept': 'application/json'}, data=message)


def _get_url():
    if current_app.config["BACKSTAGE_API_URL"] is None:
        raise KeyError("Back stage configuration URL not available.")

    return f'{current_app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message'


def _get_jwt():
    token = session.get('token')
    logger.debug(f"Retrieving current token for user {current_user.id}")
    return token
