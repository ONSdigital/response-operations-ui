import logging

from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
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
        'source': source
    })

    if not form_valid and source == 'home':
        redirect_url = url_for('respondent_bp.respondent_home')
    else:
        redirect_url = urljoin(url_for('respondent_bp.respondent_search', page=page), '?' + query_string)

    return redirect(redirect_url)


@respondent_bp.route('/search')
@respondent_bp.route('/search/')
@login_required
def alias_search_routes():
    return redirect(urljoin(url_for('respondent_bp.respondent_search'), '1'))


@respondent_bp.route('/search/<page>', methods=['GET'])
@login_required
def respondent_search(page):
    form = SearchForm()
    breadcrumbs = [{"title": "Respondents"}, {"title": "Search"}]

    args = get_controller_args_from_request(request)

    respondents = party_controller.search_respondents(args['email_address'], args['first_name'], args['last_name'], page)
    filtered_respondents = filter_respondents(respondents)
  
    render_template('respondent-search-results.html',
                    form=form, breadcrumb=breadcrumbs,
                    respondents=filtered_respondents)


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
