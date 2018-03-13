import logging
import requests

from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_respondent_details(party_id):
    logger.debug("Get respondent enrolments")
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/party-details?respondent_party_id={party_id}'
    response = requests.get(url)

    if response.status_code != 200:
        raise ApiError(response)

    return response.json()
