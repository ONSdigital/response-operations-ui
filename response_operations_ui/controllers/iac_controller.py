import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def get_iac(iac):
    logger.debug('Retrieving iac')
    if not iac:
        logger.warning('No iac provided')
        return None

    url = f'{app.config["IAC_URL"]}/iacs/{iac}'
    response = requests.get(url, auth=app.config['IAC_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.warning('IAC code not found')
            return
        logger.error('Error retrieving iac')
        raise ApiError(response)

    logger.debug('Successfully retrieved iac')
    return response.json()


def get_latest_active_iac_code(cases, collection_exercises):
    ces_ids = [ce['id'] for ce in collection_exercises]
    cases_for_survey = [case
                        for case in cases
                        if case.get('caseGroup', {}).get('collectionExerciseId') in ces_ids]
    cases_for_survey_ordered = sorted(cases_for_survey, key=lambda c: c['createdDateTime'], reverse=True)
    iac = next((case.get('iac')
                for case in cases_for_survey_ordered
                if _is_iac_active(case.get('iac'))), None)
    return iac


def _is_iac_active(iac):
    iac_response = get_iac(iac)
    return iac_response.get('active') if iac_response else None
