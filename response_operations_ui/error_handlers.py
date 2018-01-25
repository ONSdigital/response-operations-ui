import logging
from os import getenv

from flask import redirect, url_for
from requests import RequestException
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


@app.errorhandler(ApiError)
def api_error(error):
    logger.error('Api failed to retrieve required data', url=error.url,
                 status_code=str(error.status_code), exc_info=error)
    return redirect(url_for('error_bp.server_error_page',
                            _external=True,
                            _scheme=getenv('SCHEME', 'http')))


@app.errorhandler(RequestException)
def connection_error(error):
    logger.error('Failed to connect to external service', url=error.request.url)
    return redirect(url_for('error_bp.server_error_page',
                            _external=True,
                            _scheme=getenv('SCHEME', 'http')))


@app.errorhandler(Exception)
def server_error(error):  # pylint: disable=unused-argument
    logger.exception('Uncaught exception generated')
    return redirect(url_for('error_bp.server_error_page',
                            _external=True,
                            _scheme=getenv('SCHEME', 'http')))
