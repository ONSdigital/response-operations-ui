import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))

reporting_units_mock_bp = Blueprint('reporting_units_mock_bp', __name__,
                                    static_folder='static', template_folder='templates/reporting-units-mock')


@reporting_units_mock_bp.route('/', methods=['GET'])
@login_required
def reporting_units_mock():
    return render_template('reporting-units-mock.html')
