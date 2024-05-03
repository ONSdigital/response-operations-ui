import logging
import time
from json import JSONDecodeError

import jwt
import requests
from flask import current_app, session
from flask_login import current_user
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.common import token_decoder
from response_operations_ui.exceptions.exceptions import ApiError, InternalError

logger = wrap_logger(logging.getLogger(__name__))


def get_conversation(thread_id):
    logger.info("Retrieving thread", thread_id=thread_id)

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/threads/{thread_id}'

    response = requests.get(url, headers={"Authorization": _get_jwt()})

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


def get_conversation_count(survey_id, conversation_tab, business_id, category):
    logger.info(
        "Retrieving count of threads", survey_id=survey_id, conversation_tab=conversation_tab, business_id=business_id
    )

    response = _get_conversation_counts(
        business_id, conversation_tab, survey_id, category, all_conversation_types=False
    )
    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Thread count failed")
        raise ApiError(response)

    logger.info("Count successful")
    try:
        return response.json()["total"]
    except KeyError:
        logger.exception("Response was successful but didn't contain a 'total' key")
        raise


def get_all_conversation_type_counts(survey_id, conversation_tab, business_id, category):
    """Gets the count for the current tab and the count for the conversations in all 4 tabs"""
    logger.info(
        "Retrieving count of threads for all conversation tabs",
        survey_id=survey_id,
        conversation_tab=conversation_tab,
        business_id=business_id,
        category=category,
    )

    response = _get_conversation_counts(business_id, conversation_tab, survey_id, category, all_conversation_types=True)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Thread count failed")
        raise ApiError(response)

    logger.info("Count successful")

    try:
        totals = response.json()["totals"]

        # Secure Message uses different identifiers to the tab names used in the ui, this translates the names
        if "new_respondent_conversations" in totals:
            totals["initial"] = totals.pop("new_respondent_conversations")
        if "my_conversations" in totals:
            totals["my messages"] = totals.pop("my_conversations")

        totals["current"] = totals[conversation_tab]

        return totals
    except KeyError:
        logger.exception("Response was successful but didn't contain a 'totals' key")
        raise


def _get_conversation_counts(business_id, conversation_tab, survey_id, category, all_conversation_types):
    """Gets the count of conversations based on the params"""
    params = _get_secure_message_threads_params(
        survey_id, business_id, conversation_tab, category, all_conversation_types
    )
    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/messages/count'
    response = requests.get(url, headers={"Authorization": _get_jwt()}, params=params)
    return response


def _get_secure_message_threads_params(
    survey_id, business_id, conversation_tab, category, all_conversation_types=False
):
    """creates a params dictionary"""
    params = {
        "is_closed": "true" if conversation_tab == "closed" else "false",
        "my_conversations": "true" if conversation_tab == "my messages" else "false",
        "new_respondent_conversations": "true" if conversation_tab == "initial" else "false",
        "category": category,
        "all_conversation_types": "true" if all_conversation_types else "false",
    }
    if business_id:
        params["business_id"] = business_id
    if survey_id:
        params["survey"] = survey_id
    return params


def get_thread_list(survey_id, business_id, conversation_tab, page, limit, category) -> dict:
    logger.info(
        "Retrieving threads list", survey_id=survey_id, conversation_tab=conversation_tab, business_id=business_id
    )
    params = _get_secure_message_threads_params(survey_id, business_id, conversation_tab, category)
    params["page"] = page
    params["limit"] = limit

    url = f'{current_app.config["SECURE_MESSAGE_URL"]}/threads'
    # This will be removed once UAA is completed.  For now we need the call to sm to include
    # an Authorization in its header a JWT that includes party_id and role.

    response = requests.get(url, headers={"Authorization": _get_jwt()}, params=params)

    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception("Threads retrieval failed")
        raise ApiError(response)

    logger.info("Retrieval successful")
    try:
        messages = response.json()["messages"]
        return messages
    except KeyError:
        logger.exception("Response was successful but didn't contain a 'messages' key")
        raise


def send_message(message_json: dict):
    try:
        url = f'{current_app.config["SECURE_MESSAGE_URL"]}/messages'
        response = requests.post(
            url,
            headers={"Authorization": _get_jwt(), "Content-Type": "application/json", "Accept": "application/json"},
            data=message_json,
        )
        response.raise_for_status()
        time.sleep(30)
        logger.info("new message has been sent with response ", response=response.json())
    except KeyError as ex:
        logger.error("Message sending failed due to internal error", exc_info=True)
        raise InternalError(ex)
    except HTTPError as ex:
        logger.error("Message sending failed due to API Error", exc_info=True)
        raise ApiError(ex.response)


def patch_message(message_id: str, payload: dict):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/messages/{message_id}"

    logger.info("Patching message data", message_id=message_id, payload=payload)
    response = requests.patch(url, headers={"Authorization": _get_jwt()}, json=payload)

    try:
        response.raise_for_status()
        logger.info("Successfully patched message data", message_id=message_id)
    except HTTPError:
        logger.error("Failed to patch message data", message_id=message_id, status=response.status_code, exc_info=True)
        raise ApiError(response)


def remove_unread_label(message_id: str):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/messages/modify/{message_id}"
    data = {"label": "UNREAD", "action": "remove"}

    logger.info("Removing message unread label", message_id=message_id)
    response = requests.put(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.info("Successfully removed unread label", message_id=message_id)
    except HTTPError:
        logger.exception("Failed to remove unread label", message_id=message_id)


def add_unread_label(message_id: str):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/messages/modify/{message_id}"
    data = {"label": "UNREAD", "action": "add"}

    logger.info("Adding message unread label", message_id=message_id)
    response = requests.put(url, headers={"Authorization": _get_jwt(), "Content-Type": "application/json"}, json=data)

    try:
        response.raise_for_status()
        logger.info("Successfully added unread label", message_id=message_id)
    except HTTPError:
        logger.exception("Failed to add unread label", message_id=message_id)


def patch_thread(thread_id: str, payload: dict):
    url = f"{current_app.config['SECURE_MESSAGE_URL']}/threads/{thread_id}"

    logger.info("Patching thread data", thread_id=thread_id, payload=payload)
    response = requests.patch(url, headers={"Authorization": _get_jwt()}, json=payload)

    try:
        response.raise_for_status()
        logger.info("Successfully patched thread data", thread_id=thread_id)
    except HTTPError:
        logger.error("Failed to patch thread data", thread_id=thread_id, exc_info=True)
        raise ApiError(response)


def _get_jwt() -> str:
    token = session.get("token")
    decoded_token = token_decoder.decode_access_token(token)
    user_id = decoded_token.get("user_id")
    secret = current_app.config["SECURE_MESSAGE_JWT_SECRET"]
    sm_token = jwt.encode({"party_id": user_id, "role": "internal"}, secret, algorithm="HS256")
    logger.info("Retrieving current token for user", user_id=current_user.id)
    return sm_token
