import logging

from flask import Blueprint, render_template
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))

error_bp = Blueprint('error_bp', __name__, template_folder='templates/errors')


@error_bp.route('/500', methods=['GET'])
def server_error_page():
    return render_template('errors/500-error.html'), 500
