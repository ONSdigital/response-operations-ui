import json
import logging

import requests
from flask import current_app as app
from google.auth.exceptions import GoogleAuthError
from structlog import wrap_logger

from response_operations_ui.common.credentials import fetch_and_apply_oidc_credentials
from response_operations_ui.exceptions.error_codes import (
    ErrorCode,
    get_error_code_message,
)
from response_operations_ui.exceptions.exceptions import ExternalApiError

from response_operations_ui.common.connection_helper import get_response_content

logger = wrap_logger(logging.getLogger(__name__))

TARGET_SERVICE = "cir"


def get_cir_service_status():
    return _get_response_content(app.config["CIR_API_URL"] + "/status")


def get_cir_metadata(survey_ref, formtype):
    # form_type is not parameterised as it is currently the only accepted classifier type
    cir_url_query_parameters = (
        f"?classifier_type=form_type&classifier_value={formtype}&language=en&survey_id={survey_ref}"
    )
    return _get_response_content(app.config["CIR_API_URL"] + app.config["CIR_API_PREFIX"] + cir_url_query_parameters)


def _get_response_content(request_url):
    session = requests.Session()
    client_id = app.config["CIR_OAUTH2_CLIENT_ID"]
    logger.info(f"{TARGET_SERVICE} service request", request_url=request_url)

    try:
        fetch_and_apply_oidc_credentials(session=session, client_id=client_id)
    except GoogleAuthError as e:
        logger.error(
            get_error_code_message(ErrorCode.API_OIDC_CREDENTIALS_ERROR),
            client_id=client_id,
            error=str(e),
            target_service=TARGET_SERVICE,
        )
        raise ExternalApiError(None, ErrorCode.API_OIDC_CREDENTIALS_ERROR, TARGET_SERVICE) from e
    
    return get_response_content(request_url, TARGET_SERVICE, session)
