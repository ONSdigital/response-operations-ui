import logging

import requests
from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def get_iac_details(iac):
    logger.info('Retrieving iac')
    if not iac:
        logger.warning('No iac provided')
        return None

    url = f'{app.config["IAC_URL"]}/iacs/{iac}'
    response = requests.get(url, auth=app.config['BASIC_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.warning('IAC code not found')
            return
        logger.error('Error retrieving iac')
        raise ApiError(response)

    logger.info('Successfully retrieved iac')
    return response.json()


def is_iac_active(iac):
    iac_response = get_iac_details(iac)
    return iac_response.get('active') if iac_response else None
