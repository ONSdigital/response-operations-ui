import logging

from flask import Blueprint, flash, redirect, render_template, url_for
from structlog import wrap_logger
from response_operations_ui.exceptions.exceptions import ApiError, UpdateContactDetailsException


logger = wrap_logger(logging.getLogger(__name__))

error_bp = Blueprint('error_bp', __name__, template_folder='templates/errors')


@error_bp.route('/500', methods=['GET'])
def server_error_page():
    return render_template('errors/500-error.html'), 500


@error_bp.app_errorhandler(UpdateContactDetailsException)
def update_details_exception(error=None):
    logger.error('update details error', ru_ref=error.ru_ref, status_code=error.status_code)
    error_type = 'email conflict' if error.status_code == 409 else 'api error'

    return render_template('edit-contact-details.html',
                           ru_ref=error.ru_ref,
                           form=error.form,
                           error_type=error_type,
                           respondent_details=error.respondent_details)


@error_bp.app_errorhandler(ApiError)
def api_error(error):
    logger.error('Api failed to retrieve required data', message=error.message, url=error.url,
                 status=str(error.status_code))
    return redirect(url_for('error_bp.server_error_page'))


@error_bp.app_errorhandler(401)
def handle_authentication_error(error):
    logger.warn('Authentication failed')
    flash('Incorrect username or password', category='failed_authentication')
    return redirect(url_for('sign_in_bp.sign_in'))


@error_bp.app_errorhandler(Exception)
def server_error(error):  # pylint: disable=unused-argument
    logger.exception('Generic exception generated')
    return redirect(url_for('error_bp.server_error_page'))


@error_bp.app_errorhandler(500)
def server_error_500(error):  # pylint: disable=unused-argument
    return redirect(url_for('error_bp.server_error_page'))
