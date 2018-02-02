import logging
from urllib.parse import urlencode

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))

reporting_units_mock_bp = Blueprint('reporting_units_mock_bp', __name__,
                                    static_folder='static', template_folder='templates')


@reporting_units_mock_bp.route('/', methods=['GET'])
@login_required
def reporting_units_mock():
    reporting_unit = {'survey': 'BRES 2017',
                      'ru_ref': '36509908341B',
                      'business': 'Bolts & Rachets Ltd',
                      'to': 'Jacky Turner'}
    return render_template('reporting-units-mock.html',
                           args=urlencode(reporting_unit))
