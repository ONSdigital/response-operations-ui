import logging

from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask import current_app as app
from flask_login import login_required
from flask_paginate import Pagination
from structlog import wrap_logger
from urllib.parse import urlencode, urljoin

from response_operations_ui.controllers import party_controller
from response_operations_ui.forms import SearchForm
from response_operations_ui.common.respondent_utils import filter_respondents, get_controller_args_from_request


logger = wrap_logger(logging.getLogger(__name__))

respondent_bp = Blueprint('respondent_bp', __name__,
                          static_folder='static', template_folder='templates')


@respondent_bp.route('/', methods=['GET'])
@login_required
def respondent_home():
    return render_template('respondent-search/search-respondents.html',
                           form=SearchForm(),
                           breadcrumbs=[{"title": "Respondents"}])


@respondent_bp.route('/search', methods=['POST'])
@login_required
def search_redirect():
    form = SearchForm()
    form_valid = form.validate()

    if not form_valid:
        flash('At least one input should be filled')

    source = form.source.data or 'home'
    page = request.args.get('page', 1)

    query_string = urlencode({
        'email_address': form.email_address.data or '',
        'first_name': form.first_name.data or '',
        'last_name': form.last_name.data or '',
        'source': source,
        'page': page
    })

    if not form_valid and source == 'home':
        redirect_url = url_for('respondent_bp.respondent_home')
    else:
        redirect_url = urljoin(url_for('respondent_bp.respondent_search'), '?' + query_string)

    return redirect(redirect_url)


@respondent_bp.route('/search')
@respondent_bp.route('/search/', methods=['GET'])
@login_required
def respondent_search():
    breadcrumbs = [{"title": "Respondents"}, {"title": "Search"}]

    args = get_controller_args_from_request(request)

    first_name = args['first_name']
    last_name = args['last_name']
    email_address = args['email_address']
    page = args['page']

    form = SearchForm()

    form.first_name.data = first_name
    form.last_name.data = last_name
    form.email_address.data = email_address

    party_response = party_controller.search_respondents(first_name, last_name, email_address, page)

    respondents = party_response.get('data', [])
    total_respondents_available = party_response.get('total', 0)

    filtered_respondents = filter_respondents(respondents)

    RESULTS_PER_PAGE = app.config["PARTY_RESPONDENTS_PER_PAGE"]

    offset = (int(page) - 1) * RESULTS_PER_PAGE

    first_index = 1 + offset
    last_index = RESULTS_PER_PAGE + offset

    pagination = Pagination(page=int(page),
                            per_page=RESULTS_PER_PAGE,
                            total=total_respondents_available,
                            record_name='respondents',
                            prev_label='Previous',
                            next_label='Next',
                            outer_window=0,
                            format_total=True,
                            format_number=True,
                            show_single_page=False)

    return render_template('respondent-search/search-respondents-results.html',
                           form=form, breadcrumb=breadcrumbs,
                           respondents=filtered_respondents,
                           respondent_count=total_respondents_available,
                           first_index=first_index,
                           last_index=last_index,
                           pagination=pagination)


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
