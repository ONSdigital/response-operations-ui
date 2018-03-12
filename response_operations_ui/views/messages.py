import json
import logging

from flask import Blueprint, flash, g, render_template, request, redirect, url_for
from flask_login import login_required, current_user
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

    if "create-message" in request.form:
        form = _populate_hidden_form_fields_from_post(form, request.form)
        form = _populate_form_details_from_hidden_fields(form)
    elif form.validate_on_submit():
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
        'msg_from': current_user.id,
        'msg_to': [form.hidden_to_uuid.data],
        'subject': form.subject.data,
        'body': form.body.data,
        'thread_id': "",
        'collection_case': "",
        # TODO Make this UUID for v2 api
        'survey': form.hidden_survey_id.data,
        'ru_id': form.hidden_to_ru_id.data})


def _populate_hidden_form_fields_from_post(current_view_form, calling_form):
    """
    :param current_view_form: is the form just create when land in the view
    :param calling_form: is the form that is actually sent from the caller
    :return: a form with all the hidden data filled in.
    """
    try:
        current_view_form.hidden_survey.data = calling_form['survey']
        current_view_form.hidden_survey_id.data = calling_form['survey_id']
        current_view_form.hidden_ru_ref.data = calling_form['ru_ref']
        current_view_form.hidden_business.data = calling_form['business']
        current_view_form.hidden_to_uuid.data = calling_form['msg_to']
        current_view_form.hidden_to.data = calling_form['msg_to_name']
        current_view_form.hidden_to_ru_id.data = calling_form['ru_id']
    except KeyError as ex:
        logger.exception("Failed to load create message page")
        raise InternalError(ex)
    return current_view_form


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


@messages_bp.route('/threads/<thread_id>', methods=['GET'])
@login_required
def view_conversation(thread_id):
    try:
        thread_conversation = message_controllers.get_conversation(thread_id)['messages']
        refined_thread = [_refine(message) for message in reversed(thread_conversation)]
    except KeyError as ex:
        logger.exception("A key error occurred")
        raise ApiError(ex)
    breadcrumbs = [
        {"title": "Messages", "link": "/messages"},
        {"title": refined_thread[0]["subject"]}
    ]

    return render_template("conversation-view.html", breadcrumbs=breadcrumbs, messages=refined_thread)


def _get_message_subject(thread):
    try:
        subject = thread["subject"]
        return subject
    except KeyError:
        logger.exception("Failed to retrieve Subject from thread")
        return None


def _refine(message):
    return {
        'ru_ref': message.get('@ru_id').get('sampleUnitRef'),
        'thread_id': message.get('thread_id'),
        'business_name': message.get('@ru_id').get('name'),
        'subject': _get_message_subject(message),
        'from': _get_from_name(message),
        'to': _get_to_name(message),
        'sent_date': message.get('sent_date').split(".")[0],
        'body': message.get('body'),
        'internal': message.get('from_internal'),
        'username': message.get('@msg_from', dict()).get('emailAddress'),
        # TODO use survey ref instead of survey id
        'survey': message.get('survey')
    }


def _get_from_name(message):
    try:
        msg_from = message['@msg_from']
        return f"{msg_from.get('firstName')} {msg_from.get('lastName')}"
    except KeyError:
        return message.get('msg_from')


def _get_to_name(message):
    try:
        name = message.get('@msg_to')[0].get('firstName') + ' ' + message.get('@msg_to')[0].get('lastName')
    except IndexError:
        name = message.get('msg_to')[0]
    return name


