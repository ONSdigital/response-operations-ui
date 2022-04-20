import logging
from datetime import datetime, timedelta
from json import JSONDecodeError, dumps

import requests
from flask import abort
from flask import current_app as app
from flask import session
from itsdangerous import URLSafeSerializer
from requests import HTTPError
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def sign_in(username, password):
    logger.info("Retrieving OAuth2 token for sign-in")
    url = f'{app.config["UAA_SERVICE_URL"]}/oauth/token'

    data = {
        "grant_type": "password",
        "client_id": app.config["UAA_CLIENT_ID"],
        "client_secret": app.config["UAA_CLIENT_SECRET"],
        "username": username,
        "password": password,
        "response_type": "token",
        "token_format": "jwt",
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }

    response = requests.post(url, data=data, headers=headers)

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 401:
            abort(401)
        logger.exception("Failed to retrieve access token", status_code=response.status_code)
        raise

    try:
        logger.info("Successfully retrieved UAA token")
        token = response.json()
        access_token = token["access_token"]
        return access_token
    except KeyError:
        logger.exception("No access_token claim in jwt")
        abort(401)
    except (JSONDecodeError, ValueError):
        logger.exception("Error decoding JSON response")
        abort(500)


def login_admin():
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    payload = {"grant_type": "client_credentials", "response_type": "token", "token_format": "opaque"}
    try:
        url = f"{app.config['UAA_SERVICE_URL']}/oauth/token"
        response = requests.post(
            url, headers=headers, params=payload, auth=(app.config["UAA_CLIENT_ID"], app.config["UAA_CLIENT_SECRET"])
        )
        resp_json = response.json()
        return resp_json.get("access_token")
    except HTTPError:
        logger.exception("Failed to log into UAA", status_code=response.status_code)
        abort(response.status_code)


def get_user_by_email(email, access_token=None):
    if access_token is None:
        access_token = login_admin()

    headers = generate_headers(access_token)

    url = f"{app.config['UAA_SERVICE_URL']}/Users?filter=email+eq+%22{email}%22"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except HTTPError:
        url_safe_serializer = URLSafeSerializer(app.config["SECRET_KEY"])
        logger.error(
            "Error retrieving user from UAA",
            status_code=response.status_code,
            encoded_email=url_safe_serializer.dumps(email),
        )
        return

    return response.json()


def get_user_by_id(user_id: str) -> dict:
    """
    Gets the user details from uaa, using the id of the user.

    :param user_id: The id of the user in uaa
    :return: The user details from uaa in dictionary form.
    """
    access_token = login_admin()
    headers = generate_headers(access_token)

    url = f"{app.config['UAA_SERVICE_URL']}/Users/{user_id}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except HTTPError:
        logger.error("Error retrieving user from UAA", status_code=response.status_code, user_id=user_id)
        return

    return response.json()


def retrieve_user_code(access_token, username):
    headers = generate_headers(access_token)

    url = f"{app.config['UAA_SERVICE_URL']}/password_resets"
    response = requests.post(url, headers=headers, data=username)

    if response.status_code != 201:
        logger.error("Error received when asking UAA for a password reset code", status_code=response.status_code)
        return

    return response.json().get("code")


def change_password(access_token, user_code, new_password):
    headers = generate_headers(access_token)

    payload = {"code": user_code, "new_password": new_password}

    url = f"{app.config['UAA_SERVICE_URL']}/password_change"
    return requests.post(url, data=dumps(payload), headers=headers)


def generate_headers(access_token):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    return headers


def change_user_password(email, password):
    access_token = login_admin()

    user_response = get_user_by_email(email, access_token)
    if user_response is None:
        return
    username = user_response["resources"][0]["userName"]

    password_reset_code = retrieve_user_code(access_token=access_token, username=username)
    if password_reset_code is None:
        return

    return change_password(access_token=access_token, user_code=password_reset_code, new_password=password)


def create_user_account(email, password, user_name, first_name, last_name):
    access_token = login_admin()

    headers = generate_headers(access_token)

    payload = {
        "userName": user_name,
        "name": {"formatted": f"{first_name} {last_name}", "givenName": first_name, "familyName": last_name},
        "emails": [{"value": email, "primary": True}],
        "active": True,
        "verified": True,
        "password": password,
    }

    url = f"{app.config['UAA_SERVICE_URL']}/Users"
    response = requests.post(url, data=dumps(payload), headers=headers)
    try:
        response.raise_for_status()
        return
    except HTTPError:
        if response.status_code == 409:
            # Username already exists
            errors = {"user_name": ["Username already in use; please choose another"]}
        else:
            errors = {"status_code": response.status_code, "message": response.reason}
            logger.error(
                "Received an error when creating an account in UAA",
                status_code=response.status_code,
                reason=response.reason,
            )

    return errors


def update_user_account(payload):
    """
    Updates the user in uaa, using the user's id

    :param payload: the same payload we receive from uaa, with the updated values
    :return errors: The errors returned from uaa as a dictionary
    """
    access_token = login_admin()

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "If-Match": str(payload["meta"]["version"]),
    }
    logger.info("Attempting change of user information")
    url = f"{app.config['UAA_SERVICE_URL']}/Users/{payload['id']}"
    response = requests.put(url, data=dumps(payload), headers=headers)
    try:
        response.raise_for_status()
        return
    except HTTPError:
        if response.status_code == 404:
            # User id not found
            errors = {"user_id": ["User id not found"]}
        elif response.status_code == 400:
            # Username already exists
            errors = {"status_code": response.status_code, "message": "Username already in use"}
        else:
            errors = {"status_code": response.status_code, "message": "Unknown error"}
            logger.error(
                "Received an error when updating account in UAA",
                status_code=response.status_code,
                reason=response.reason,
            )

    return errors


def update_user_password(user, old_password, new_password):
    """
    Updates the user password in uaa, using the user's id
    :param user - UAA user object.
    :param old_password
    :param new_password
    :return errors: The errors returned from uaa as a dictionary
    """
    access_token = login_admin()
    headers = generate_headers(access_token)
    payload = {"oldPassword": old_password, "password": new_password}
    logger.info("Attempting change of user's password")
    url = f"{app.config['UAA_SERVICE_URL']}/Users/{user['id']}/password"
    response = requests.put(url, data=dumps(payload), headers=headers)
    try:
        response.raise_for_status()
        return
    except HTTPError:
        if response.status_code == 404:
            # User id not found
            errors = {"user_id": ["User id not found"]}
        elif response.status_code == 400:
            errors = {"status_code": response.status_code, "message": "Invalid JSON format or missing fields"}
        elif response.status_code == 401:
            errors = {"status_code": response.status_code, "message": "Invalid current password "}
        else:
            errors = {"status_code": response.status_code, "message": response.reason}
            logger.error(
                "Received an error when updating account in UAA",
                status_code=response.status_code,
                reason=response.reason,
            )

    return errors


def refresh_permissions(user_id):
    """
    Refreshes the cache of permissions for the current user
    :param user_id: The user ID to refresh for
    """
    user = get_user_by_id(user_id)
    session["permissions"] = {"groups": user.get("groups"), "expiry": (datetime.now() + timedelta(minutes=5))}


def user_has_permission(permission, user_id=None) -> bool:
    """
    Checks to see if the user provided or in the session has the specified permission
    :param permission: The permission to check
    :param user_id: An optional user ID to check for
    :return has_permission: Whether the user has the permission or not
    """
    # Feature flagged
    is_role_based_access_enabled = app.config["IS_ROLE_BASED_ACCESS_ENABLED"]
    if not is_role_based_access_enabled:
        default_permissions = [
            "surveys.edit",
            "reportingunits.edit",
            "respondents.edit",
            "respondents.delete",
            "messages.edit",
        ]
        return permission in default_permissions

    if user_id is None:
        if session is None or "user_id" not in session:
            return False
        user_id = session["user_id"]

    if "permissions" not in session or session["permissions"]["expiry"] < datetime.now():
        refresh_permissions(user_id)

    return any(permission in g["display"] for g in session["permissions"]["groups"])


def get_users_list(
    start_index: int, max_count: int, query: str = None, sort_by: str = "email", sort_order: str = "ascending"
):
    """
    Gets all users in rops and provides a list.
    :param query - UAA user object.
    :param sort_by
    :param sort_order
    :param start_index
    :param max_count
    :return errors: The errors returned from uaa as a dictionary
    """
    access_token = login_admin()
    headers = generate_headers(access_token)
    param = {"filter": query, "sortBy": sort_by, "count": max_count, "startIndex": start_index, "sortOrder": sort_order}
    logger.info("Attempting to fetch user records")
    url = f"{app.config['UAA_SERVICE_URL']}/Users"
    response = requests.get(url, params=param, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except HTTPError:
        logger.error("Unauthorised attempt to get user list.", status_code=response.status_code)
        raise "Unauthorised Access"


def get_filter_query(filter_criteria: str, filter_value: str, filter_on: str):
    return f"{filter_on} {get_filter(filter_criteria)} '{filter_value}'"


def get_filter(filter_criteria: str):
    switch = {
        "equal": "eq",
        "contains": "co",
        "starts with": "sw",
        "present": "pr",
    }
    return switch.get(filter_criteria, "nothing")
