import json
import logging

import requests
from flask import current_app as app
from google.auth.exceptions import GoogleAuthError
from structlog import wrap_logger

from response_operations_ui.common.credentials import fetch_and_apply_oidc_credentials
from response_operations_ui.exceptions.exceptions import ExternalApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_cir_service_status():

    session = requests.Session()
    client_id = app.config["CIR_OAUTH2_CLIENT_ID"]
    request_url = app.config["CIR_API_URL"] + "/status"
    logger.debug("Get service status", session_headers=str(session.headers), request_url=request_url)

    try:
        fetch_and_apply_oidc_credentials(session=session, client_id=client_id)
    except GoogleAuthError as e:
        logger.error("Fetching and applying OIDC credentials", client_id=client_id, error=str(e))
        raise ExternalApiError(None, "CIR0005: Fetching OIDC credentials error: " + str(e))

    try:
        response = session.get(request_url)
    except requests.ConnectionError as e:
        logger.error("Service connection error", error=str(e), request_url=request_url)
        raise ExternalApiError(None, "CIR0001: CIR service connection error: " + str(e))

    if response.status_code != 200:
        logger.error(
            "Service returned unexpected status code", status_code=str(response.status_code), request_url=request_url
        )
        raise ExternalApiError(
            response, "CIR0002: CIR service returned unexpected status code: " + str(response.status_code)
        )
    if response.headers.get("content-type") == "application/json":
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error("Service returned unexpected content in response", error=str(e), request_url=request_url)
            raise ExternalApiError(response, "CIR0003: CIR service returned unexpected content in response: " + str(e))
    else:
        logger.error(
            "Service returned unexpected content-type",
            content_type=response.headers.get("content-type"),
            request_url=request_url,
        )
        raise ExternalApiError(
            response,
            "CIR0004: CIR service returned unexpected content-type: " + str(response.headers.get("content-type")),
        )
