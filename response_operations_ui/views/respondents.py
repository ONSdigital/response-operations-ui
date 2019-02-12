import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import party_controller
from response_operations_ui.forms import SearchForm


logger = wrap_logger(logging.getLogger(__name__))

respondent_bp = Blueprint('respondent_bp', __name__,
                          static_folder='static', template_folder='templates')


@respondent_bp.route('/', methods=['GET', 'POST'])
@login_required
def respondent_search():
    form = SearchForm()
    breadcrumbs = [{"title": "Respondents"}]
    response = None

    if request.method == 'POST':
        email_address = request.form.get('email_address')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not form.validate():
            return render_template('respondent-search/search-respondents.html', validation_error='At least one input should be filled', response=response, form=form, breadcrumbs=breadcrumbs)

        respondents = party_controller.search_respondents(email_address, first_name, last_name)
        if respondents:
            return render_template('respondent-search/search-respondents-results.html', respondents=respondents, respondent_count=len(respondents))
        else:
            return render_template('respondent-search/search-respondents-results.html', respondents=[], respondent_count=0)

    return render_template('respondent-search/search-respondents.html', response=response, form=form, breadcrumbs=breadcrumbs)


@respondent_bp.route('/respondent-details/<respondent_id>', methods=['GET'])
@login_required
def respondent_details(respondent_id):

    respondent = party_controller.get_respondent_by_party_id(respondent_id)
    enrolments = party_controller.get_respondent_enrolments(respondent)

    breadcrumbs = [
        {
            "title": "Respondents",
            "link": "/respondents"
        },
        {
            "title": f"{respondent['emailAddress']}"
        }
    ]

    respondent['status'] = respondent['status'].title()
    return render_template('respondent.html', respondent=respondent, enrolments=enrolments, breadcrumbs=breadcrumbs)
