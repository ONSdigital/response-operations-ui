import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import reporting_units_controllers


logger = wrap_logger(logging.getLogger(__name__))

reporting_unit_bp = Blueprint('reporting_unit_bp', __name__, static_folder='static', template_folder='templates')


@reporting_unit_bp.route('/<ru_ref>', methods=['GET'])
@login_required
def view_reporting_unit(ru_ref):
    reporting_unit = reporting_units_controllers.get_reporting_unit(ru_ref)
    breadcrumbs = [
        {
            "title": "Reporting units",
            "link": "/reporting-units"
        },
        {
            "title": f"{ru_ref}"
        }
    ]
    return render_template('reporting-unit.html', ru=reporting_unit, breadcrumbs=breadcrumbs)
