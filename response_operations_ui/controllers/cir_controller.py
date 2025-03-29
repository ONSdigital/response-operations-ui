import json
import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui.common.credentials import fetch_and_apply_oidc_credentials

logger = wrap_logger(logging.getLogger(__name__))


def get_cir_service_status():
    logger.info("Getting CIR service status")
    session = requests.Session()
    fetch_and_apply_oidc_credentials(session=session, client_id=app.config["CIR_OAUTH2_CLIENT_ID"])
    logger.info(f"session.headers: {str(session.headers)}")

    try:
        response = session.get(app.config["CIR_API_URL"] + "/status")
    except requests.ConnectionError as e:
        raise HTTPError("CIR service status request failed: " + str(e))

    if response.status_code != 200:
        raise HTTPError("CIR service returned status code " + str(response.status_code))
    if response.headers.get("content-type") == "application/json":
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            raise HTTPError("Failed to decode CIR status response as JSON")
    else:
        logger.error("CIR status returned invalid content type")
        raise HTTPError("CIR status returned invalid content type " + response.headers.get("content-type"))
