import logging
from json import JSONDecodeError

import jwt
import requests
from flask import current_app, session
from flask_login import current_user
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.common import token_decoder
from response_operations_ui.exceptions.exceptions import ApiError, NoMessagesError, InternalError


logger = wrap_logger(logging.getLogger(__name__))


def get_conversation(thread_id):
    logger.info("Retrieving thread", thread_id=thread_id)

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/threads/{thread_id}'

    response = requests.get(url, headers={'Authorization': _get_jwt()})

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        logger.exception("Thread retrieval failed", thread_id=thread_id)
        raise ApiError(response)
    logger.info("Thread retrieval successful", thread_id=thread_id)

    try:
        return response.json()
    except JSONDecodeError:
        logger.exception("Response could not be decoded", thread_id=thread_id)
        raise ApiError(response)


def get_conversation_count(survey_id, conversation_tab, business_id):
    logger.info("Retrieving count of threads")

    params = _get_secure_message_threads_params(survey_id, business_id, conversation_tab)

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/messages/count'

    response = requests.get(url, headers={'Authorization': _get_jwt()}, params=params)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Thread count failed")
        raise ApiError(response)

    logger.info("Count successful")
    try:
        return response.json()['total']
    except KeyError:
        logger.exception("Response was successful but didn't contain a 'total' key")
        raise NoMessagesError


def _get_secure_message_threads_params(survey_id, business_id, conversation_tab):
    """creates a params dictionary based on data passed in"""
    params = {'survey_id': survey_id,
              'is_closed': 'true' if conversation_tab == 'closed' else 'false',
              'my_conversations': 'true' if conversation_tab == 'my messages' else 'false',
              'new_respondent_conversations': 'true' if conversation_tab == 'initial' else 'false'}
    if business_id:
        params['ru_id'] = business_id   #TODO: Change me to business_id
    return params


def get_thread_list(survey_id, business_id, conversation_tab,  page, limit):

    logger.info("Retrieving threads list")
    params = _get_secure_message_threads_params(survey_id, business_id, conversation_tab)
    params['page'] = page
    params['limit'] = limit
       
    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/threads'
    # This will be removed once UAA is completed.  For now we need the call to sm to include
    # an Authorization in its header a JWT that includes party_id and role.

    response = requests.get(url, headers={'Authorization': _get_jwt()}, params=params)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Threads retrieval failed")
        raise ApiError(response)

    logger.info("Retrieval successful")
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
        logger.error("Message sending failed due to internal error", exc_info=True)
        raise InternalError(ex)
    except HTTPError as ex:
        logger.error("Message sending failed due to API Error", exc_info=True)
        raise ApiError(ex.response)


def remove_unread_label(message_id):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/messages/modify/{message_id}"
    data = {"label": "UNREAD", "action": "remove"}

    logger.info("Removing message unread label", message_id=message_id)
    response = requests.put(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.info("Successfully removed unread label", message_id=message_id)
    except HTTPError:
        logger.exception("Failed to remove unread label", message_id=message_id)


def add_unread_label(message_id):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/messages/modify/{message_id}"
    data = {"label": "UNREAD", "action": "add"}

    logger.info("Adding message unread label", message_id=message_id)
    response = requests.put(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.info("Successfully added unread label", message_id=message_id)
    except HTTPError:
        logger.exception("Failed to add unread label", message_id=message_id)


def update_close_conversation_status(thread_id, status):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/threads/{thread_id}"
    data = {"is_closed": status}

    logger.info("Updating close conversation status", thread_id=thread_id, status=status)
    response = requests.patch(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.info("Successfully updated close conversation status", thread_id=thread_id, status=status)
    except HTTPError:
        logger.error("Failed to update close conversation status", thread_id=thread_id, status=status, exc_info=True)
        raise ApiError(response)

def _post_new_message(message):
    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/messages'
    return requests.post(url, headers={'Authorization': _get_jwt(), 'Content-Type': 'application/json',
                                       'Accept': 'application/json'}, data=message)


def _get_jwt():
    token = session.get('token')
    decoded_token = token_decoder.decode_access_token(token)
    user_id = decoded_token.get('user_id')
    secret = current_app.config['RAS_SECURE_MESSAGING_JWT_SECRET']
    sm_token = jwt.encode({'party_id': user_id, 'role': 'internal'}, secret, algorithm='HS256')
    logger.info("Retrieving current token for user", user_id=current_user.id)
    return sm_token
