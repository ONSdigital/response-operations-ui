import logging

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
    ru_details = reporting_units_controllers.get_reporting_unit(ru_ref)

    ru_details['surveys'] = sorted(ru_details['surveys'], key=lambda survey: survey['surveyRef'])

    for survey in ru_details['surveys']:
        survey['collection_exercises'] = sorted(survey['collection_exercises'],
                                                key=lambda ce: ce['scheduledStartDateTime'],
                                                reverse=True)

        for collection_exercise in survey['collection_exercises']:
            collection_exercise['responseStatus'] = map_ce_response_status(collection_exercise['responseStatus'])
            collection_exercise['companyRegion'] = map_region(collection_exercise['companyRegion'])

        for respondent in survey['respondents']:
            respondent['status'] = respondent['status'].title()
            respondent['enrolmentStatus'] = respondent['enrolmentStatus'].title()

    breadcrumbs = [
        {
            "title": "Reporting units",
            "link": "/reporting-units"
        },
        {
            "title": f"{ru_ref}"
        }
    ]

    return render_template('reporting-unit.html', ru=ru_details['reporting_unit'],
                           surveys=ru_details['surveys'],
                           breadcrumbs=breadcrumbs)


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


def map_ce_response_status(ce_response_status):
    if ce_response_status == "NOTSTARTED":
        ce_response_status = "Not started"
    elif ce_response_status == "COMPLETE":
        ce_response_status = "Completed"
    elif ce_response_status == "INPROGRESS":
        ce_response_status = "In progress"

    return ce_response_status


def map_region(region):
    if region == "YY":
        region = "NI"
    else:
        region = "GB"

    return region
