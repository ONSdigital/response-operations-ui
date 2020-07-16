import logging

from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask import current_app as app
from flask_login import login_required
from flask_paginate import Pagination
from structlog import wrap_logger
from response_operations_ui.common.respondent_utils import edit_contact, filter_respondents
from response_operations_ui.controllers import party_controller, reporting_units_controllers
from response_operations_ui.forms import RespondentSearchForm, EditContactDetailsForm


logger = wrap_logger(logging.getLogger(__name__))

respondent_bp = Blueprint('respondent_bp', __name__,
                          static_folder='static', template_folder='templates')


@respondent_bp.route('/', methods=['GET'])
@login_required
def respondent_home():
    return render_template('respondent-search/respondent-search.html',
                           form=RespondentSearchForm(),
                           breadcrumbs=[{"text": "Respondents"}])


@respondent_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_redirect():
    form = RespondentSearchForm()
    form_valid = form.validate()

    if not form_valid:
        flash('At least one input should be filled')
        return redirect(url_for('respondent_bp.respondent_home'))

    email_address = form.email_address.data or ''
    first_name = form.first_name.data or ''
    last_name = form.last_name.data or ''

    breadcrumbs = [{"text": "Respondents"}, {"text": "Search"}]

    page = request.values.get('page', '1')
    limit = app.config["PARTY_RESPONDENTS_PER_PAGE"]

    party_response = party_controller.search_respondents(first_name, last_name, email_address, page, limit)

    respondents = party_response.get('data', [])
    total_respondents_available = party_response.get('total', 0)

    filtered_respondents = filter_respondents(respondents)

    results_per_page = app.config["PARTY_RESPONDENTS_PER_PAGE"]

    offset = (int(page) - 1) * results_per_page

    last_index = (results_per_page + offset) if total_respondents_available >= results_per_page \
        else total_respondents_available

    pagination = Pagination(page=int(page),
                            per_page=results_per_page,
                            total=total_respondents_available,
                            record_name='respondents',
                            prev_label='Previous',
                            next_label='Next',
                            outer_window=0,
                            format_total=True,
                            format_number=True,
                            show_single_page=False)

    return render_template('respondent-search/respondent-search-results.html',
                           form=form, breadcrumb=breadcrumbs,
                           respondents=filtered_respondents,
                           respondent_count=total_respondents_available,
                           first_index=1 + offset,
                           last_index=last_index,
                           pagination=pagination,
                           show_pagination=bool(total_respondents_available > results_per_page))


@respondent_bp.route('/respondent-details/<respondent_id>', methods=['GET'])
@login_required
def respondent_details(respondent_id):

    respondent = party_controller.get_respondent_by_party_id(respondent_id)
    enrolments = party_controller.get_respondent_enrolments(respondent)

    breadcrumbs = [
        {
            "text": "Respondents",
            "url": "/respondents"
        },
        {
            "text": f"{respondent['emailAddress']}"
        }
    ]

    respondent['status'] = respondent['status'].title()

    info = request.args.get('info')
    if request.args.get('enrolment_changed'):
        flash('Enrolment status changed', 'information')
    if request.args.get('account_status_changed'):
        flash('Account status changed', 'information')
    elif info:
        flash(info, 'information')

    return render_template('respondent.html', respondent=respondent, enrolments=enrolments, breadcrumbs=breadcrumbs)


@respondent_bp.route('/edit-contact-details/<respondent_id>', methods=['GET'])
@login_required
def view_contact_details(respondent_id):
    respondent_details = party_controller.get_respondent_by_party_id(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_details)

    return render_template('edit-contact-details.html', respondent_details=respondent_details, form=form,
                           tab='respondents', respondent_id=respondent_id)


@respondent_bp.route('/edit-contact-details/<respondent_id>', methods=['POST'])
@login_required
def edit_contact_details(respondent_id):
    edit_contact(respondent_id)
    return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent_id,
                            message_key='details_changed'))


@respondent_bp.route('/resend_verification/<respondent_id>', methods=['GET'])
@login_required
def view_resend_verification(respondent_id):
    logger.info("Re-send verification email requested", respondent_id=respondent_id)
    respondent = party_controller.get_respondent_by_party_id(respondent_id)
    email = respondent['pendingEmailAddress'] if 'pendingEmailAddress' in respondent else respondent['emailAddress']

    return render_template('re-send-verification-email.html', respondent_id=respondent_id, email=email,
                           tab='respondents')


@respondent_bp.route('/resend_verification/<party_id>', methods=['POST'])
@login_required
def resend_verification(party_id):
    reporting_units_controllers.resend_verification_email(party_id)
    logger.info("Re-sent verification email.", party_id=party_id)
    flash('Verification email re-sent')
    return redirect(url_for('respondent_bp.respondent_details', respondent_id=party_id,))


@respondent_bp.route('<respondent_id>/change-enrolment-status', methods=['POST'])
@login_required
def change_enrolment_status(respondent_id):
    reporting_units_controllers.change_enrolment_status(business_id=request.args['business_id'],
                                                        respondent_id=respondent_id,
                                                        survey_id=request.args['survey_id'],
                                                        change_flag=request.args['change_flag'])
    return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent_id, enrolment_changed='True'))


@respondent_bp.route('/<respondent_id>/change-respondent-status', methods=['POST'])
@login_required
def change_respondent_status(respondent_id):
    reporting_units_controllers.change_respondent_status(respondent_id=respondent_id,
                                                         change_flag=request.args['change_flag'])
    return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent_id,
                            account_status_changed='True'))


@respondent_bp.route('/<party_id>/change-respondent-status', methods=['GET'])
@login_required
def confirm_change_respondent_status(party_id):
    respondent = party_controller.get_respondent_by_party_id(party_id)
    return render_template('confirm-respondent-status-change.html',
                           respondent_id=respondent['id'],
                           first_name=respondent['firstName'],
                           last_name=respondent['lastName'],
                           email_address=respondent['emailAddress'],
                           change_flag=request.args['change_flag'],
                           tab='respondents')
