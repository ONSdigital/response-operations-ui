import logging
from json import JSONDecodeError

import requests
from flask import abort, current_app as app
from requests import HTTPError
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))


def sign_in(username, password):
    logger.debug('Retrieving OAuth2 token for sign-in')
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
        logger.debug('Successfully retrieved UAA token')
        token = response.json()
        access_token = token['access_token']
        return access_token
    except KeyError:
        logger.exception("No access_token claim in jwt")
        abort(401)
    except (JSONDecodeError, ValueError):
        logger.exception("Error decoding JSON response")
        abort(500)
