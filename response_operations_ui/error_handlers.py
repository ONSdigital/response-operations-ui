import logging

from requests import RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


@app.errorhandler(ApiError)
def api_error(error):
    logger.error('Api failed to retrieve required data', url=error.url,
                 status_code=str(error.status_code), exc_info=error)
    return "FAIL"


@app.errorhandler(RequestException)
def connection_error(error):
    logger.error('Failed to connect to external service', url=error.request.url)
    return "FAIL"
