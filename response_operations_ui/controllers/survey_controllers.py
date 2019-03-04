import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from config import FDI_LIST
from response_operations_ui.common.mappers import format_short_name
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def get_survey_by_id(survey_id):
    logger.debug("Retrieve survey using survey id", survey_id=survey_id)
    url = f'{app.config["SURVEY_URL"]}/surveys/{survey_id}'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Survey retrieval failed", survey_id=survey_id)
        raise ApiError(response)

    logger.debug("Successfully retrieved survey", survey_id=survey_id)
    return response.json()


def get_survey_by_shortname(short_name):
    short_name = ''.join(short_name.split())
    logger.debug('Retrieving survey', short_name=short_name)
    url = f'{app.config["SURVEY_URL"]}/surveys/shortname/{short_name}'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error retrieving survey', short_name=short_name)
        raise ApiError(response)

    logger.debug('Successfully retrieved survey', short_name=short_name)
    return response.json()


def get_survey_ci_classifier(survey_id):
    logger.debug('Retrieving classifier type selectors', survey_id=survey_id)
    url = f'{app.config["SURVEY_URL"]}/surveys/{survey_id}/classifiertypeselectors'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    if response.status_code == 204:
        logger.error('classifiers missing for survey', survey_id=survey_id)
        raise ApiError(response)
    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error classifier type selectors', survey_id=survey_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved classifier type selectors', survey_id=survey_id)

    classifier_type_selectors = response.json()
    ci_selector = None
    for selector in classifier_type_selectors:
        if selector['name'] == "COLLECTION_INSTRUMENT":
            ci_selector = selector
            break

    logger.debug('Retrieving classifiers for CI selector type', survey_id=survey_id, ci_selector=ci_selector['id'])
    url = f'{app.config["SURVEY_URL"]}/surveys/{survey_id}/classifiertypeselectors/{ci_selector["id"]}'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error retrieving classifiers for CI selector type', survey_id=survey_id,
                     ci_selector=ci_selector['id'])
        raise ApiError(response)

    logger.debug('Successfully retrieved classifiers for CI selector type', survey_id=survey_id,
                 ci_selector=ci_selector['id'])

    return response.json()


def get_surveys_list():
    logger.debug('Retrieving surveys list')
    url = f'{app.config["SURVEY_URL"]}/surveys/surveytype/Business'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    if response.status_code == 204:
        logger.debug('No surveys found in survey service')
        return []

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error retrieving the survey list')
        raise ApiError(response)

    logger.debug('Successfully retrieved surveys list')
    survey_list = response.json()
    # Format survey shortName
    for survey in survey_list:
        survey['shortName'] = format_short_name(survey['shortName'])
    # Order List by surveyRef
    return sorted(survey_list, key=lambda k: k['surveyRef'])


def get_survey(short_name):
    survey = get_survey_by_shortname(short_name)
    logger.debug('Getting survey details', short_name=short_name, survey_id=survey['id'])

    # Format survey shortName
    survey['shortName'] = format_short_name(survey['shortName'])

    logger.debug('Successfully retrieved survey details', short_name=short_name, survey_id=survey['id'])
    return survey


def convert_specific_fdi_survey_to_fdi(survey_short_name):
    for fdi_survey in FDI_LIST:
        if survey_short_name == fdi_survey:
            return "FDI"
    return survey_short_name


def get_surveys_dictionary():
    surveys_list = get_surveys_list()
    return {survey['id']: {'shortName': convert_specific_fdi_survey_to_fdi(survey.get('shortName')),
                           'surveyRef': survey.get('surveyRef')}
            for survey in surveys_list}


def get_grouped_surveys_list():
    survey_set = {convert_specific_fdi_survey_to_fdi(survey['shortName']) for survey in get_surveys_list()}
    return sorted(survey_set)


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

    return get_survey_by_shortname(short_name)['id']


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
    url = f'{app.config["SURVEY_URL"]}/surveys/ref/{survey_ref}'

    survey_details = {
        "ShortName": short_name,
        "LongName": long_name
    }

    response = requests.put(url, json=survey_details, auth=app.config['SURVEY_AUTH'])

    if response.status_code == 404:
        logger.warning('Error retrieving survey details', survey_ref=survey_ref)
        raise ApiError(response)
    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Failed to update survey details', survey_ref=survey_ref)
        raise ApiError(response)

    logger.debug('Successfully updated survey details', survey_ref=survey_ref)


def get_legal_basis_list():
    logger.debug('Retrieving legal basis list')
    url = f'{app.config["SURVEY_URL"]}/legal-bases'
    response = requests.get(url, auth=app.config['SURVEY_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Failed retrieving legal basis list')
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
        "legalBasisRef": legal_basis,
        "surveyType": "Business"
    }

    response = requests.post(url, json=survey_details, auth=app.config['SURVEY_AUTH'])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error('Error creating new survey',
                     survey_ref=survey_ref, short_name=short_name,
                     long_name=long_name, legal_basis=legal_basis,
                     status_code=response.status_code)
        raise ApiError(response)

    logger.debug('Successfully created new survey', survey_ref=survey_ref)
