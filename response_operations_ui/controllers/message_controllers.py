import logging
import jwt
import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_message_list():

    #token = jwt.encode
    logger.debug("Retrieving Message list")
    url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
    response = requests.get(url, headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE1MTc4Mjk0NTYsImV4cCI6MTU0OTM2NTQ1NiwiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoianJvY2tldEBleGFtcGxlLmNvbSIsInBhcnR5X2lkIjoiQlJFUyIsInJvbGUiOiJpbnRlcm5hbCJ9.8MzPQvULms45V5bGa_DeipNgyYbS_jOeXAcHnq3dImE'})
    if response.status_code != 200:
        raise ApiError(response)

    logger.debug("Retrieve success")

    return response.json()