import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import party_controller
from response_operations_ui.forms import Confirm, SearchForm


logger = wrap_logger(logging.getLogger(__name__))
respondent_bp = Blueprint('respondent_bp', __name__,
                          static_folder='static', template_folder='templates')


@respondent_bp.route('/', methods=['GET', 'POST'])
@login_required
def respondent_search():
    form = SearchForm()
    breadcrumbs = [{"title": "Respondents"}]
    response = None

    if form.validate_on_submit():
        email = request.form.get('query')

        respondent = party_controller.search_respondent_by_email(email)

        if respondent.get('id'):
            return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent['id']))
        else:
            response = respondent['Response']

    return render_template('search-respondent.html', response=response, form=form, breadcrumbs=breadcrumbs)


@respondent_bp.route('/respondent-details/<respondent_id>', methods=['GET'])
@login_required
def respondent_details(respondent_id):

    respondent = party_controller.get_respondent_by_party_id(respondent_id)

    breadcrumbs = [
        {
            "title": "Respondents",
            "link": "/respondents"
        },
        {
            "title": f"{respondent['firstName']} {respondent['lastName']}"
        }
    ]

    respondent['status'] = respondent['status'].title()
    return render_template('respondent.html', respondent=respondent['respondent_party'], breadcrumbs=breadcrumbs)


@respondent_bp.route('/confirm-change-respondent-account-status', methods=['GET'])
@login_required
def confirm_change_account_status():
    party_id = request.args['party_id']
    change_status = request.args['change_status']
    ru_ref = request.args['ru_ref'] if request.args['ru_ref'] else None
    form = Confirm(request.form)

    respondent = party_controller.get_respondent_by_party_id(party_id)
    enrolments = party_controller.get_respondent_enrolments(respondent, enrolment_status='ENABLED')

    return render_template('confirm-respondent-account-status.html', form=form,
                           respondent=respondent, enrolments=enrolments,
                           change_status=change_status, party_id=party_id, ru_ref=ru_ref)


@respondent_bp.route('/change-respondent-account-status', methods=['POST'])
@login_required
def change_account_status():
    party_id = request.args['party_id']
    change_status = request.args['change_status']
    ru_ref = request.args['ru_ref']
    party_controller.change_respondent_account_status(party_id, change_status)
    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref, info='Account status changed'))
