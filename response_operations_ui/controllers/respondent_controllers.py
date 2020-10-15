import base64
import logging

import requests
from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def search_respondent_by_email(email):
    logger.info('Searching for respondent by email')

    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/email'
    response = requests.get(url, json={'email': email}, auth=app.config['BASIC_AUTH'])

    if response.status_code == 404:
        logger.info("No respondent found for email address", status_code=response.status_code)
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception("Respondent retrieval failed")
        raise ApiError(response)
    logger.info("Respondent retrieved by email successfully")

    return response.json()


def find_respondent_account_by_username(username):
    logger.info('Finding respondent account')
    auth = "{}:{}".format(app.config["SECURITY_USER_NAME"], app.config["SECURITY_USER_PASSWORD"]).encode('utf-8')
    headers = {
        'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")
    }
    url = f'{app.config["AUTH_URL"]}/api/account/user/{username}'
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve user', email=obfuscate_email(username))
        raise ApiError(response)
    logger.info('Successfully retrieve user', email=obfuscate_email(username))
    return response.json()


def delete_respondent_account_by_username(username):
    logger.info('Marking respondent for deletion')
    auth = "{}:{}".format(app.config["SECURITY_USER_NAME"], app.config["SECURITY_USER_PASSWORD"]).encode('utf-8')
    headers = {
        'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")
    }
    url = f'{app.config["AUTH_URL"]}/api/account/user'
    form_data = {"username": username}
    response = requests.delete(url, data=form_data, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to mark respondent for deletion', username=obfuscate_email(username))
        raise ApiError(response)
    logger.info('Successfully marked respondent for deletion', username=obfuscate_email(username))


def undo_delete_respondent_account_by_username(username):
    logger.info('Restating respondent marked for deletion')
    auth = "{}:{}".format(app.config["SECURITY_USER_NAME"], app.config["SECURITY_USER_PASSWORD"]).encode('utf-8')
    headers = {
        'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")
    }
    url = f'{app.config["AUTH_URL"]}/api/account/user/{username}'
    form_data = {"mark_for_deletion": False}
    response = requests.patch(url, data=form_data, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to undo respondent mark for deletion', username=obfuscate_email(username))
        raise ApiError(response)
    logger.info('Successfully restated respondent', username=obfuscate_email(username))


def obfuscate_email(email):
    """Takes an email address and returns an obfuscated version of it.
    For example: test@example.com would turn into t**t@e*********m
    """
    m = email.split('@')
    prefix = f'{m[0][0]}{"*" * (len(m[0]) - 2)}{m[0][-1]}'
    domain = f'{m[1][0]}{"*" * (len(m[1]) - 2)}{m[1][-1]}'
    return f'{prefix}@{domain}'
