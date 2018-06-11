from json import JSONDecodeError
import logging
import jwt

from flask import current_app, session
from flask_login import current_user
import requests
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError, NoMessagesError, InternalError
from response_operations_ui.common import token_decoder

logger = wrap_logger(logging.getLogger(__name__))


def get_conversation(thread_id):
    logger.debug("Retrieving thread")

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/v2/threads/{thread_id}'

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


def get_conversation_count(params):
    logger.debug("Retrieving count of threads")

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/v2/messages/count'

    response = requests.get(url, headers={'Authorization': _get_jwt()}, params=params)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Thread count failed")
        raise ApiError(response)

    logger.debug("Count successful")
    try:
        return response.json()['total']
    except KeyError:
        logger.exception("Response was successful but didn't contain a 'total' key")
        raise NoMessagesError


def get_thread_list(params):
    logger.debug("Retrieving threads list")

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/threads'
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


def remove_unread_label(message_id):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/v2/messages/modify/{message_id}"
    data = {"label": "UNREAD", "action": "remove"}

    logger.debug("Removing message unread label", message_id=message_id)
    response = requests.put(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.debug("Successfully removed unread label", message_id=message_id)
    except HTTPError:
        logger.exception("Failed to remove unread label", message_id=message_id)


def add_closed_conversation_label(thread_id):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/v2/threads/{thread_id}"
    data = {"is_closed": True}

    logger.debug("Adding closed conversation label", thread_id=thread_id)
    response = requests.patch(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.debug("Successfully added closed conversation label", thread_id=thread_id)
    except HTTPError:
        logger.exception("Failed to add closed conversation label", thread_id=thread_id)
        raise ApiError(response)


def remove_closed_conversation_label(thread_id):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/v2/threads/{thread_id}"
    data = {"is_closed": False}

    logger.debug("Removing closed conversation label", thread_id=thread_id)
    response = requests.patch(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.debug("Successfully removed closed conversation label", thread_id=thread_id)
    except HTTPError:
        logger.exception("Failed to remove closed conversation label", thread_id=thread_id)
        raise ApiError(response)


def _post_new_message(message):
    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/v2/messages'
    return requests.post(url, headers={'Authorization': _get_jwt(), 'Content-Type': 'application/json',
                                       'Accept': 'application/json'}, data=message)


def _get_jwt():
    token = session.get('token')
    decoded_token = token_decoder.decode_access_token(token)
    user_id = decoded_token.get('user_id')
    secret = current_app.config['RAS_SECURE_MESSAGING_JWT_SECRET']
    sm_token = jwt.encode({'party_id': user_id, 'role': 'internal'}, secret, algorithm='HS256')
    logger.debug(f"Retrieving current token for user {current_user.id}")
    return sm_token
