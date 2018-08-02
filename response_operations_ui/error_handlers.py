import logging

from flask import flash, redirect, url_for
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError


logger = wrap_logger(logging.getLogger(__name__))


def api_error(error):
    logger.error('Api failed to retrieve required data', message=error.message, url=error.url,
                 status=str(error.status_code))
    return redirect(url_for('error_bp.server_error_page'))


def handle_authentication_error(error):
    logger.warn('Authentication failed')
    flash('Incorrect username or password', category='failed_authentication')
    return redirect(url_for('sign_in_bp.sign_in'))


def server_error(error):  # pylint: disable=unused-argument
    logger.exception('Generic exception generated')
    return redirect(url_for('error_bp.server_error_page'))


def server_error_500(error):  # pylint: disable=unused-argument
    return redirect(url_for('error_bp.server_error_page'))


def setup_error_handlers(app):
    app.register_error_handler(ApiError, api_error)
    app.register_error_handler(401, handle_authentication_error)
    app.register_error_handler(Exception, server_error)
    app.register_error_handler(500, server_error_500)
    return app
