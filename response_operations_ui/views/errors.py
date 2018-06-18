import logging

from flask import Blueprint, render_template
from structlog import wrap_logger
from response_operations_ui.exceptions.exceptions import UpdateContactDetailsException

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
