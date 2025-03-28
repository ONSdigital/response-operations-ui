import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError
from structlog import wrap_logger

from response_operations_ui.common.credentials import fetch_and_apply_oidc_credentials

logger = wrap_logger(logging.getLogger(__name__))


def get_cir_service_status():
    session = requests.Session()
    fetch_and_apply_oidc_credentials(session=session, client_id=app.config["CIR_OAUTH2_CLIENT_ID"])
    logger.info(f"session.headers: {str(session.headers)}")
    response = session.get(app.config["CIR_API_URL"] + "/status")
    if response.status_code != 200:
        logger.error("CIR service is not available")
        raise HTTPError("CIR service is not available")
    logger.info("Getting CIR service status")
    return {"status": 200}
