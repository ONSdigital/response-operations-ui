import json
import logging

from flask import Blueprint, flash, g, render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import message_controllers
from response_operations_ui.exceptions.exceptions import ApiError, InternalError, NoMessagesError
from response_operations_ui.forms import SecureMessageForm

logger = wrap_logger(logging.getLogger(__name__))
messages_bp = Blueprint('messages_bp', __name__,
                        static_folder='static', template_folder='templates')


@messages_bp.route('/create-message', methods=['POST'])
@login_required
def create_message():
    form = SecureMessageForm(request.form)
    breadcrumbs = _build_create_message_breadcrumbs()

    if not form.is_submitted() and 'create-message-view' in request.form:
        form = _populate_hidden_form_fields_from_post(form, request.form)
        form = _populate_form_details_from_hidden_fields(form)

    if form.validate_on_submit():

        # Keep the message subject and body
        g.form_subject_data = form.subject.data
        g.form_body_data = form.body.data

        try:
            message_controllers.send_message(_get_message_json(form))
            flash("Message sent.")
            return redirect(url_for('messages_bp.view_messages'))
        except (ApiError, InternalError):
            form = _repopulate_form_with_submitted_data(form)
            form.errors['sending'] = ["Message failed to send, something has gone wrong with the website."]
            return render_template('create-message.html',
                                   form=form,
                                   breadcrumbs=breadcrumbs)

    return render_template('create-message.html',
                           form=form,
                           breadcrumbs=breadcrumbs)


def _build_create_message_breadcrumbs():
    return [
        {"title": "Messages", "link": "/messages"},
        {"title": "Create Message"}
    ]


def _repopulate_form_with_submitted_data(form):
    form.survey.text = form.hidden_survey.data
    form.ru_ref.text = form.hidden_ru_ref.data
    form.business.text = form.hidden_business.data
    form.to.text = form.hidden_to.data
    form.body.data = g.form_body_data
    form.subject.data = g.form_subject_data
    return form


def _get_message_json(form):
    return json.dumps({
        'msg_from': "BRES",
        'msg_to': ["f62dfda8-73b0-4e0e-97cf-1b06327a6712"],
        'subject': form.subject.data,
        'body': form.body.data,
        'thread_id': "",
        'collection_case': "CC_PLACEHOLDER",
        'survey': form.hidden_survey.data,
        'ru_id': "c614e64e-d981-4eba-b016-d9822f09a4fb"})


def _populate_hidden_form_fields_from_post(current_view_form, calling_form):
    """
    :param current_view_form: it sthe form just create when land in the view
    :param calling_form: is the form that is actually sent from the caller
    :return: a form with all the hidden data filled in.
    """
    current_view_form.hidden_survey.data = calling_form.survey.data
    current_view_form.hidden_ru_ref.data = calling_form.ru_ref.data
    current_view_form.hidden_business.data = calling_form.msg_to_name.data
    current_view_form.hidden_to.data = calling_form.msg_to.data
    return current_view_form


def _populate_hidden_form_fields_from_url_params(form, ru_dict):
    form.hidden_survey.data = ru_dict.get('survey')[0]
    form.hidden_ru_ref.data = ru_dict.get('ru_ref')[0]
    form.hidden_business.data = ru_dict.get('business')[0]
    form.hidden_to.data = ru_dict.get('to')[0]
    form.hidden_to_uuid.data = ru_dict.get('to_uuid')[0]
    form.hidden_to_ru_id.data = ru_dict.get('to_ru_id')[0]
    return form


def _populate_form_details_from_hidden_fields(form):
    form.survey.text = form.hidden_survey.data
    form.ru_ref.text = form.hidden_ru_ref.data
    form.business.text = form.hidden_business.data
    form.to.text = form.hidden_to.data
    return form


@messages_bp.route('/', methods=['GET'])
@login_required
def view_messages():
    # Currently the filtering is only being done with parameters.  In the future, the session
    # will have the a list of survey_ids the user is allowed to see and the parameters for the
    # backstage call can be populated by looking at the session instead of http parameters.
    params = {
        'label': request.args.get('label'),
        'survey': request.args.get('survey')
    }
    breadcrumbs = [{"title": "Messages"}]
    try:
        messages = message_controllers.get_message_list(params)
        refined_messages = [_refine(msg) for msg in messages]
        return render_template("messages.html", breadcrumbs=breadcrumbs, messages=refined_messages)
    except NoMessagesError:
        return render_template("messages.html", breadcrumbs=breadcrumbs, response_error=True)


def _refine(message):
    return {
        'ru_ref': message.get('ru_id'),
        'business_name': message.get('@ru_id').get('name'),
        'subject': message.get('subject'),
        'from': message.get('msg_from'),
        'to': message.get('@msg_to')[0].get('firstName') + ' ' + message.get('@msg_to')[0].get('lastName'),
        'sent_date': message.get('sent_date')
    }
