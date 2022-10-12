import logging
from urllib.parse import urlencode

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.exceptions.exceptions import (
    ApiError,
    RURetrievalError,
    SearchRespondentsException,
    UpdateContactDetailsException,
)
from response_operations_ui.forms import EditContactDetailsForm

logger = wrap_logger(logging.getLogger(__name__))


def get_business_by_ru_ref(ru_ref: str):
    """
    Get business by ru_ref

    :param ru_ref: The ru_ref of the business
    :type ru_ref: str
    :return: A dict of data about the business
    :rtype: dict
    :raises ApiError: Raised if party returns a 4XX or 5XX status code.
    """
    logger.info("Retrieving reporting unit", ru_ref=ru_ref)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/ref/{ru_ref}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Failed to retrieve reporting unit", ru_ref=ru_ref)
        if response.status_code == 404:
            raise RURetrievalError(response, ru_ref)
        else:
            raise ApiError(response)

    logger.info("Successfully retrieved reporting unit", ru_ref=ru_ref)
    return response.json()


def get_business_attributes_by_party_id(business_party_id: str, collection_exercise_ids=None):
    """
    Gets the attributes for the business for each collection exercise.  The attributes are the data held
    on the business at the point it was enrolled onto each collection exercise.  If no exercises are specified
    then all attributes for the business will be returned

    :param business_party_id: A business id
    :param collection_exercise_ids: An (optional) list of collection exercise ids
    :type collection_exercise_ids: list
    :return: A dict of attributes with each collection exercise id as the keys.
    :rtype: dict
    """
    bound_logger = logger.bind(business_id=business_party_id, collection_exercise_ids=collection_exercise_ids)
    bound_logger.info("Retrieving business attributes")
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/id/{business_party_id}/attributes'
    if collection_exercise_ids:
        params = urlencode([("collection_exercise_id", uuid) for uuid in collection_exercise_ids])
        response = requests.get(url, params=params, auth=app.config["BASIC_AUTH"])
    else:
        response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bound_logger.error("Error retrieving business attributes")
        raise ApiError(response)

    bound_logger.info("Successfully retrieved business attributes")
    return response.json()


def get_business_by_party_id(business_party_id: str, collection_exercise_id=None):
    logger.info(
        "Retrieving business party", business_party_id=business_party_id, collection_exercise_id=collection_exercise_id
    )
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/id/{business_party_id}'
    params = {"collection_exercise_id": collection_exercise_id, "verbose": True}
    response = requests.get(url, params=params, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level(
            "Error retrieving business party",
            business_party_id=business_party_id,
            collection_exercise_id=collection_exercise_id,
        )
        raise ApiError(response)

    logger.info(
        "Successfully retrieved business party",
        business_party_id=business_party_id,
        collection_exercise_id=collection_exercise_id,
    )
    return response.json()


def get_respondent_by_party_id(respondent_party_id):
    logger.info("Retrieving respondent party", respondent_party_id=respondent_party_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_party_id}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Error retrieving respondent party", respondent_party_id=respondent_party_id)
        if response.status_code == 404:
            return {}
        raise ApiError(response)

    logger.info("Successfully retrieved respondent party", respondent_party_id=respondent_party_id)
    return response.json()


def get_pending_surveys_by_party_id(respondent_party_id):
    logger.info("Retrieving pending surveys", respondent_party_id=respondent_party_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/pending-surveys/originator/{respondent_party_id}'
    response = requests.get(url, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Error retrieving pending surveys", respondent_party_id=respondent_party_id)
        if response.status_code == 404:
            return {}
        raise ApiError(response)

    logger.info("Successfully retrieved pending surveys", respondent_party_id=respondent_party_id)
    return response.json()


def delete_pending_surveys_by_batch_number(batch_number):
    logger.info("Deleting pending surveys", batch_number=batch_number)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/pending-surveys/{batch_number}'
    response = requests.delete(url, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Error deleting pending survey", batch_number=batch_number)
        raise ApiError(response)

    logger.info("Successfully deleted pending surveys", batch_number=batch_number)


def resend_pending_surveys_email(batch_number):
    logger.info("Resending pending survey email", batch_number=batch_number)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/pending-surveys/resend-email'
    response = requests.post(url, json={"batch_number": batch_number}, auth=app.config["BASIC_AUTH"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level("Error sending pending survey email", batch_number=batch_number)
        return {}

    logger.info("Successfully resend pending survey email", batch_number=batch_number)
    return response.json()


def get_respondent_by_party_ids(uuids):
    """
    Gets data for multiple respondents from party.  If the list is empty, returns an empty
    list without going to party.

    This call will return as many parties as it can find.  If some are missing, no error will
    be thrown.

    :param uuids: A list of uuid strings of respondent party ids
    :type uuids: list
    :return: A list of dicts containing party data
    """
    bound_logger = logger.bind(respondent_party_ids=uuids)
    bound_logger.info("Retrieving respondent data for multiple respondents")
    if not uuids:
        bound_logger.info("No party uuids provided.  Returning empty list")
        return []

    params = urlencode([("id", uuid) for uuid in uuids])
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents'
    response = requests.get(url, auth=app.config["BASIC_AUTH"], params=params)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bound_logger.error("Error retrieving respondent data for multiple respondents")
        raise ApiError(response)

    bound_logger.info("Successfully retrieved respondent data for multiple respondents")
    return response.json()


def survey_ids_for_respondent(respondent, ru_ref):
    enrolments = [
        association.get("enrolments")
        for association in respondent.get("associations")
        if association["sampleUnitRef"] == ru_ref
    ][0]
    return [enrolment.get("surveyId") for enrolment in enrolments]


def add_enrolment_status_for_respondent(respondent, ru_ref, survey_id):
    logger.info("Adding enrolment status to respondent", ru_ref=ru_ref)
    association = next(
        (association for association in respondent.get("associations") if association["sampleUnitRef"] == ru_ref), None
    )
    enrolment_status = next(
        (
            enrolment["enrolmentStatus"]
            for enrolment in association.get("enrolments")
            if enrolment["surveyId"] == survey_id
        ),
        None,
    )
    return {**respondent, "enrolmentStatus": enrolment_status}


def get_respondent_enrolments(respondent: dict, enrolment_status=None) -> list:
    enrolments = []
    if "associations" in respondent:
        for association in respondent["associations"]:
            business_party = get_business_by_party_id(association["partyId"])
            for enrolment in association["enrolments"]:
                enrolment_data = {
                    "business": business_party,
                    "survey": get_survey_by_id(enrolment["surveyId"]),
                    "status": enrolment["enrolmentStatus"],
                }
                if enrolment_status:
                    if enrolment_data["status"] == enrolment_status:
                        enrolments.append(enrolment_data)
                else:
                    enrolments.append(enrolment_data)

    return enrolments


def search_respondent_by_email(email):
    logger.info("Search respondent via email")

    request_json = {"email": email}
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/email'
    response = requests.get(url, json=request_json, auth=app.config["BASIC_AUTH"])

    if response.status_code == 404:
        return

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code == 400 else logger.exception
        log_level("Respondent retrieval failed")
        raise ApiError(response)
    logger.info("Respondent retrieved successfully")

    return response.json()


def search_respondents(first_name, last_name, email_address, page, limit):
    params = {
        "firstName": first_name,
        "lastName": last_name,
        "emailAddress": email_address,
        "page": page,
        "limit": limit,
    }
    response = requests.get(
        f'{app.config["PARTY_URL"]}/party-api/v1/respondents', auth=app.config["BASIC_AUTH"], params=params
    )

    if response.status_code != 200:
        raise SearchRespondentsException(
            response, first_name=first_name, last_name=last_name, email_address=email_address, page=page
        )

    return response.json()


def update_contact_details(respondent_id, form, ru_ref="NOT DEFINED"):
    logger.info("Updating respondent details", respondent_id=respondent_id, ru_ref=ru_ref)

    new_contact_details = {
        "firstName": form.get("first_name"),
        "lastName": form.get("last_name"),
        "email_address": form.get("hidden_email"),
        "new_email_address": form.get("email").strip(),
        "telephone": form.get("telephone"),
    }

    old_contact_details = get_respondent_by_party_id(respondent_id)
    contact_details_changed = _compare_contact_details(new_contact_details, old_contact_details)

    if len(contact_details_changed) > 0:
        url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_id}'
        response = requests.put(url, json=new_contact_details, auth=app.config["BASIC_AUTH"])

        if response.status_code != 200:
            raise UpdateContactDetailsException(
                ru_ref, EditContactDetailsForm(form), old_contact_details, response.status_code
            )

        logger.info(
            "Respondent details updated", respondent_id=respondent_id, status_code=response.status_code, ru_ref=ru_ref
        )

    return contact_details_changed


def delete_attributes_by_sample_summary_id(sample_summary_id: str) -> None:
    """
    Deletes all the business attributes for a given sample_summary_id.  Each attribute represents a sample that a
    business was part of, and if the sample is deleted (e.g., a mistake was made in the sample file) then calling
    this will remove the now not needed data in party that is generated as part of the sample load process.

    :param sample_summary_id: A sample summary id
    :return: None
    :raises ApiError: Occurs in the case that party returns a 4XX or 5XX value.  The most likely case being that
    the sample_summary_id isn't a valid uuid.
    """
    logger.info("Deleting business attributes", sample_summary_id=sample_summary_id)

    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/attributes/sample-summary/{sample_summary_id}'
    response = requests.delete(url, auth=app.config["BASIC_AUTH"])

    try:
        response.raise_for_status()
    except HTTPError:
        logger.error(
            "Failed to delete business attributes by sample summary id",
            sample_summary_id=sample_summary_id,
            status_code=response.status_code,
        )
        raise ApiError(response)
    logger.info("Successfully deleted business attributes", sample_summary_id=sample_summary_id)
    return


def _compare_contact_details(new_contact_details, old_contact_details):
    # Currently the 'get contact details' and 'update respondent details' keys do not match and must be mapped
    contact_details_map = {
        "firstName": "firstName",
        "lastName": "lastName",
        "telephone": "telephone",
        "emailAddress": "new_email_address",
    }

    return {
        old_key
        for old_key, new_key in contact_details_map.items()
        if old_contact_details[old_key] != new_contact_details[new_key]
    }
