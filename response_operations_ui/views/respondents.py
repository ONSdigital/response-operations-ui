import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from structlog import wrap_logger
from response_operations_ui.controllers import party_controller, reporting_units_controllers
from response_operations_ui.forms import SearchForm, EditContactDetailsForm
from response_operations_ui.controllers.party_controller import get_respondent_by_party_id


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
        # NB: requires exact email to be entered
        respondent = party_controller.search_respondent_by_email(email)
        if respondent:
            return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent['id']))
        response = 'No Respondent found for ' + email

    return render_template('search-respondent.html', response=response, form=form, breadcrumbs=breadcrumbs)


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

    info_message = None

    info = request.args.get('info')
    if info:
        info_message = info
    if request.args.get('enrolment_changed'):
        info_message = 'Enrolment status changed'
    if request.args.get('account_status_changed'):
        info_message = 'Account status changed'

    return render_template('respondent.html', respondent=respondent, enrolments=enrolments, breadcrumbs=breadcrumbs,
                           info_message=info_message)


@respondent_bp.route('/edit-contact-details/<respondent_id>', methods=['GET'])
@login_required
def view_contact_details(respondent_id):
    respondents_details = party_controller.get_respondent_by_party_id(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondents_details)

    return render_template('edit-contact-details.html', respondent_details=respondents_details,
                           form=form, tab='respondents')


@respondent_bp.route('/edit-contact-details/<respondent_id>', methods=['POST'])
@login_required
def edit_contact_details(respondent_id):
    form = request.form
    contact_details_changed = party_controller.update_contact_details(respondent_id, form)

    ui_message = 'No updates were necessary'
    if 'emailAddress' in contact_details_changed:
        ui_message = f'Contact details changed and verification email sent to {form.get("email")}'
    elif len(contact_details_changed) > 0:
        ui_message = 'Contact details changed'

    return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent_id, info=ui_message))


@respondent_bp.route('/resend_verification/<respondent_id>', methods=['GET'])
@login_required
def view_resend_verification(respondent_id):
    logger.debug("Re-send verification email requested", respondent_id=respondent_id)
    respondent = party_controller.get_respondent_by_party_id(respondent_id)
    email = respondent['pendingEmailAddress'] if 'pendingEmailAddress' in respondent else respondent['emailAddress']

    return render_template('re-send-verification-email.html', respondent_id=respondent_id, email=email,
                           tab='respondents')


@respondent_bp.route('/resend_verification/<party_id>', methods=['POST'])
@login_required
def resend_verification(party_id):
    reporting_units_controllers.resend_verification_email(party_id)
    logger.info("Re-sent verification email.", party_id=party_id)
    return redirect(url_for('respondent_bp.respondent_details', respondent_id=party_id,
                            info='Verification email re-sent'))


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
                                                         change_flag=request.args['change_flag']),
    return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent_id, account_status_changed='True'))


@respondent_bp.route('/<party_id>/change-respondent-status', methods=['GET'])
@login_required
def confirm_change_respondent_status(party_id):
    respondent = get_respondent_by_party_id(party_id)
    return render_template('confirm-respondent-status-change.html',
                           respondent_id=respondent['id'],
                           first_name=respondent['firstName'],
                           last_name=respondent['lastName'],
                           email_address=respondent['emailAddress'],
                           change_flag=request.args['change_flag'],
                           tab='respondents')
