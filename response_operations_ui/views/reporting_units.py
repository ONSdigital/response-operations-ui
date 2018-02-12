import logging
from urllib.parse import urlencode

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import reporting_units_controllers
from response_operations_ui.forms import SearchForm


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

    # Details for mock create message link
    ru_details = {'survey': 'BRES 2017',
                  'ru_ref': ru_ref,
                  'business': 'Bolts & Rachets Ltd',
                  'to': 'Jacky Turner',
                  'to_uuid': "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                  'to_ru_id': "c614e64e-d981-4eba-b016-d9822f09a4fb"}

    return render_template('reporting-unit.html', ru=reporting_unit, breadcrumbs=breadcrumbs,
                           args=urlencode(ru_details))


@reporting_unit_bp.route('/', methods=['GET', 'POST'])
@login_required
def search_reporting_units():
    form = SearchForm(request.form)
    breadcrumbs = [{"title": "Reporting units"}]
    business_list = None

    if form.validate_on_submit():
        query = request.form.get('query')

        business_list = reporting_units_controllers.search_reporting_units(query)

    return render_template('reporting-units.html', business_list=business_list, form=form, breadcrumbs=breadcrumbs)
