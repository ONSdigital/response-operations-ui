import logging

import requests
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.common.surveys import FDISurveys
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_surveys_list():
    logger.debug('Retrieving surveys list')
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/surveys'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved surveys list')
    return response.json()


def get_survey(short_name):
    logger.debug('Retrieving survey', short_name=short_name)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname/{short_name}'

    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully retrieved survey', short_name=short_name)
    return response.json()


def convert_specific_fdi_survey_to_fdi(survey_short_name):
    for fdi_survey in FDISurveys:
        if survey_short_name == fdi_survey.value:
            return "FDI"
    return survey_short_name


def get_surveys_dictionary():
    surveys_list = get_surveys_list()
    return {survey['id']: {'shortName': convert_specific_fdi_survey_to_fdi(survey.get('shortName')),
                           'surveyRef': survey.get('surveyRef')}
            for survey in surveys_list}


def get_survey_short_name_by_id(survey_id):
    try:
        return app.surveys_dict[survey_id]['shortName']
    except (AttributeError, KeyError):
        try:
            app.surveys_dict = get_surveys_dictionary()
            return app.surveys_dict[survey_id]['shortName']
        except ApiError:
            logger.exception("Failed to resolve survey short name due to API error", survey_id=survey_id)
        except KeyError:
            logger.exception("Failed to resolve survey short name", survey_id=survey_id)


def get_survey_id_by_short_name(short_name):
    logger.debug('Retrieving survey id by short name', short_name=short_name)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname/{short_name}'

    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError(response)

    survey_data = response.json()

    return survey_data['survey']['id']


def get_survey_ref_by_id(survey_id):
    try:
        return app.surveys_dict[survey_id]['surveyRef']
    except (AttributeError, KeyError):
        try:
            app.surveys_dict = get_surveys_dictionary()
            return app.surveys_dict[survey_id]['surveyRef']
        except ApiError:
            logger.exception("Failed to resolve survey ref due to API error", survey_id=survey_id)
        except KeyError:
            logger.exception("Failed to resolve survey ref", survey_id=survey_id)


def update_survey_details(survey_ref, short_name, long_name):
    logger.debug('Updating survey details', survey_ref=survey_ref)
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/edit-survey-details/{survey_ref}'

    survey_details = {
        "short_name": short_name,
        "long_name": long_name
    }

    response = requests.put(url, json=survey_details)
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug('Successfully updated survey details', survey_ref=survey_ref)


def get_legal_basis_list():
    logger.debug('Retrieving legal basis list')
    url = f'{app.config["SURVEY_URL"]}/legal-bases'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])
    if response.status_code != 200:
        raise ApiError(response)

    lbs = [(lb['ref'], lb['longName']) for lb in response.json()]
    logger.debug('Successfully retrieved legal basis list', lbs=lbs)
    return lbs


def create_survey(survey_ref, short_name, long_name, legal_basis):
    logger.debug('Creating new survey',
                 survey_ref=survey_ref, short_name=short_name,
                 long_name=long_name, legal_basis=legal_basis)
    url = f'{app.config["SURVEY_URL"]}/surveys'

    survey_details = {
        "surveyRef": survey_ref,
        "shortName": short_name,
        "longName": long_name,
        "legalBasisRef": legal_basis
    }

    response = requests.post(
        url,
        json=survey_details,
        auth=(app.config['SURVEY_USERNAME'], app.config['SURVEY_PASSWORD']))

    if response.status_code != 201:
        logger.debug("Raising ApiError for response code {}", status_code=response.status_code)
        raise ApiError(response)

    logger.debug('Successfully created new survey', survey_ref=survey_ref)


def get_survey_by_id(survey_id):
    logger.debug("Retrieve survey using survey id", survey_id=survey_id)
    url = f'{app.config["SURVEY_URL"]}/surveys/{survey_id}'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        logger.exception("Survey retrieval failed", survey_id=survey_id)
        raise ApiError(response)

    return response.json()