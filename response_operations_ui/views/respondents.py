import logging

from flask import Blueprint, render_template, request, redirect
from flask_login import login_required
from structlog import wrap_logger
from urllib.parse import urlencode

from response_operations_ui.controllers import party_controller
from response_operations_ui.forms import SearchForm
from response_operations_ui.common.respondent_utils import filter_respondents


logger = wrap_logger(logging.getLogger(__name__))

respondent_bp = Blueprint('respondent_bp', __name__,
                          static_folder='static', template_folder='templates')


@respondent_bp.route('/', methods=['GET', 'POST'])
@login_required
def respondent_home():
    form = SearchForm()
    breadcrumbs = [{"title": "Respondents"}]

    return render_template('respondent-search/search-respondents.html',
                           form=form,
                           breadcrumbs=breadcrumbs)


@respondent_bp.route('/search', methods=['GET'])
@login_required
def respondent_search():
    form = SearchForm()
    breadcrumbs = [{"title": "Respondents"}, {"title": "Search"}]

    email_address = request.args.get('email_address', ''),
    first_name = request.args.get('first_name', ''),
    last_name = request.args.get('last_name', ''),
    page = request.args.get('page', 1)

    form.email_address.data = email_address
    form.first_name.data = first_name
    form.last_name.data = last_name
    form.page.data = page

    if not form.validate():
        return render_template( # swap for redirect.
            # TODO: Replace with a flash message
            'respondent-search/search-respondents.html',
            validation_error='At least one input should be filled',
            form=form,
            breadcrumbs=breadcrumbs)

    respondents = party_controller.search_respondents(email_address, first_name, last_name, page)
    
    render_template('respondent-search', form=form, breadcrumb=breadcrumb, filter_respondents(respondents))


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
