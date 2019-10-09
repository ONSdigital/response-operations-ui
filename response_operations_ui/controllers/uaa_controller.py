import logging
from json import JSONDecodeError, dumps

import requests
from flask import abort, current_app as app
from requests import HTTPError
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))


def sign_in(username, password):
    logger.info('Retrieving OAuth2 token for sign-in')
    url = f'{app.config["UAA_SERVICE_URL"]}/oauth/token'

    data = {
        'grant_type': 'password',
        'client_id': app.config['UAA_CLIENT_ID'],
        'client_secret': app.config['UAA_CLIENT_SECRET'],
        'username': username,
        'password': password,
        'response_type': 'token',
        'token_format': 'jwt',
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }

    response = requests.post(url, data=data, headers=headers)

    try:
        response.raise_for_status()
    except HTTPError:
        if response.status_code == 401:
            abort(401)
        logger.exception(f'Failed to retrieve access token', status_code=response.status_code)
        raise

    try:
        logger.info('Successfully retrieved UAA token')
        token = response.json()
        access_token = token['access_token']
        return access_token
    except KeyError:
        logger.exception("No access_token claim in jwt")
        abort(401)
    except (JSONDecodeError, ValueError):
        logger.exception("Error decoding JSON response")
        abort(500)


def login_admin():
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    payload = {'grant_type': 'client_credentials',
               'response_type': 'token',
               'token_format': 'opaque'}
    try:
        url = f"{app.config['UAA_SERVICE_URL']}/oauth/token"
        response = requests.post(url, headers=headers, params=payload,
                                 auth=(app.config['UAA_CLIENT_ID'], app.config['UAA_CLIENT_SECRET']))
        resp_json = response.json()
        return resp_json.get('access_token')
    except HTTPError:
        logger.exception(f'Failed to log into UAA', status_code=response.status_code)
        abort(response.status_code)


def get_user_by_email(email, access_token=None):
    if access_token is None:
        access_token = login_admin()

    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': f'Bearer {access_token}'}

    url = f"{app.config['UAA_SERVICE_URL']}/Users?filter=email+eq+%22{email}%22"
    response = requests.get(url, headers=headers)
    if response.status_code != 200 or response.json()['totalResults'] == 0:
        return

    return response.json()


def get_first_name_by_email(email):
    response = get_user_by_email(email)
    if response is not None:
        return response['resources'][0]['name']['givenName']
    return ""


def retrieve_user_code(access_token, username):
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': f'Bearer {access_token}'}

    url = f"{app.config['UAA_SERVICE_URL']}/password_resets"
    response = requests.post(url, headers=headers, data=username)

    if response.status_code != 201:
        logger.error('Error received when asking UAA for a password reset code',
                     status_code=response.status_code)
        return

    return response.json().get('code')


def change_password(access_token, user_code, new_password):
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': f'Bearer {access_token}'}

    payload = {
        "code": user_code,
        "new_password": new_password
    }

    url = f"{app.config['UAA_SERVICE_URL']}/password_change"
    return requests.post(url, data=dumps(payload), headers=headers)


def change_user_password(email, password):
    access_token = login_admin()

    user_response = get_user_by_email(email, access_token)
    if user_response is None:
        return False
    username = user_response['resources'][0]['userName']

    password_reset_code = retrieve_user_code(access_token=access_token, username=username)
    if password_reset_code is None:
        return False

    return change_password(access_token=access_token, user_code=password_reset_code,
                           new_password=password)
