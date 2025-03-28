import logging

# import requests
# from flask import current_app as app
# from requests.exceptions import ConnectionError, HTTPError, Timeout
from structlog import wrap_logger

# from config import Config
# from response_operations_ui.common.credentials import fetch_and_apply_oidc_credentials

logger = wrap_logger(logging.getLogger(__name__))


def get_cir_service_status():
    logger.info("Getting CIR service status")
    # fetch_and_apply_oidc_credentials(session=session, client_id=Config.CIR_OAUTH2_CLIENT_ID)
    return {"status": 200}
