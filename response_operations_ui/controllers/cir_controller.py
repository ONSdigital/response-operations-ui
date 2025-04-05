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

logger = wrap_logger(logging.getLogger(__name__))

TARGET_SERVICE = "CIR"


def get_cir_service_status():
    session = requests.Session()
    client_id = app.config["CIR_OAUTH2_CLIENT_ID"]
    request_url = app.config["CIR_API_URL"] + "/status"
    logger.debug("Get service status", session_headers=str(session.headers), request_url=request_url)

    try:
        fetch_and_apply_oidc_credentials(session=session, client_id=client_id)
    except GoogleAuthError as e:
        logger.error(
            get_error_code_message(ErrorCode.OIDC_CREDENTIALS_ERROR),
            client_id=client_id,
            error=str(e),
            target_service=TARGET_SERVICE,
        )
        raise ExternalApiError(None, ErrorCode.OIDC_CREDENTIALS_ERROR, TARGET_SERVICE) from e

    try:
        response = session.get(request_url)
    except requests.ConnectionError as e:
        logger.error(
            get_error_code_message(ErrorCode.CONNECTION_ERROR),
            error=str(e),
            request_url=request_url,
            target_service=TARGET_SERVICE,
        )
        raise ExternalApiError(None, ErrorCode.CONNECTION_ERROR, TARGET_SERVICE) from e

    if response.status_code != 200:
        logger.error(
            get_error_code_message(ErrorCode.UNEXPECTED_STATUS_CODE),
            status_code=str(response.status_code),
            request_url=request_url,
            target_service=TARGET_SERVICE,
        )
        raise ExternalApiError(response, ErrorCode.UNEXPECTED_STATUS_CODE, TARGET_SERVICE)
    if response.headers.get("content-type") == "application/json":
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error(
                get_error_code_message(ErrorCode.UNEXPECTED_CONTENT),
                error=str(e),
                request_url=request_url,
                target_service=TARGET_SERVICE,
            )
            raise ExternalApiError(response, ErrorCode.UNEXPECTED_CONTENT, TARGET_SERVICE) from e
    else:
        logger.error(
            get_error_code_message(ErrorCode.UNEXPECTED_CONTENT_TYPE),
            content_type=response.headers.get("content-type"),
            request_url=request_url,
            target_service=TARGET_SERVICE,
        )
        raise ExternalApiError(response, ErrorCode.UNEXPECTED_CONTENT_TYPE, TARGET_SERVICE)
