import logging
from structlog import wrap_logger
from flask import render_template, request, flash
from response_operations_ui.forms import EditContactDetailsForm
from response_operations_ui.controllers import party_controller

logger = wrap_logger(logging.getLogger(__name__))


def status_enum_to_string(status):
    enum_lookup = {
        'ACTIVE': 'Active',
        'CREATED': 'Created',
        'SUSPENDED': 'Suspended',
        'LOCKED': 'Locked'
    }
    return enum_lookup.get(status)


def status_enum_to_class(status):
    enum_lookup = {
        'ACTIVE': 'status--success',
        'CREATED': 'status--info',
        'SUSPENDED': 'status--warning',
        'LOCKED': 'status--dead'
    }
    return enum_lookup.get(status)


def filter_respondents(respondents):
    filtered_respondents = []
    for respondent in respondents:
        try:
            respondent_id = str(respondent['id'])
            filtered_respondents.append({
                'href': f'/respondents/respondent-details/{respondent_id}',
                'name': respondent['firstName'] + ' ' + respondent['lastName'],
                'email': respondent['emailAddress'],
                'status': status_enum_to_string(respondent['status']),
                'status_class': status_enum_to_class(respondent['status'])
            })
        except KeyError:
            logger.info('Could not add respondent to retrieved list, as data structure was not as expected.')
    return filtered_respondents


def edit_contact(respondent_id, ru_ref='NOT DEFINED'):
    edit_contact_details_form = EditContactDetailsForm(form=request.form)
    if not edit_contact_details_form.validate():
        contact_details = party_controller.get_respondent_by_party_id(respondent_id)
        return render_template('edit-contact-details.html', form=edit_contact_details_form, tab='respondents',
                               ru_ref=ru_ref, respondent_id=respondent_id, errors=edit_contact_details_form.errors,
                               respondent_details=contact_details)

    logger.info('Updating respondent details', respondent_id=respondent_id)
    form = request.form
    contact_details_changed = party_controller.update_contact_details(respondent_id, form, ru_ref)

    if 'emailAddress' in contact_details_changed:
        flash(f'Contact details changed and verification email sent to {form.get("email")}')
    elif len(contact_details_changed) > 0:
        flash('Contact details changed')
    else:
        flash('No updates were necessary')
