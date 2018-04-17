import json
import logging

from flask import Blueprint, flash, g, Markup, render_template, request, redirect, session, url_for
from flask_paginate import get_page_args, get_parameter, Pagination
from flask_login import login_required, current_user
from structlog import wrap_logger

from response_operations_ui.common.dates import get_formatted_date
from response_operations_ui.common.mappers import format_short_name
from response_operations_ui.common.surveys import Surveys, FDISurveys
from response_operations_ui.controllers import message_controllers, survey_controllers
from response_operations_ui.exceptions.exceptions import ApiError, InternalError, NoMessagesError
from response_operations_ui.forms import SecureMessageForm
from response_operations_ui.controllers.survey_controllers import get_survey_short_name_by_id, get_survey_ref_by_id

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
        # Keep the message subject and body when message sent
        g.form_subject_data = form.subject.data
        g.form_body_data = form.body.data

        try:
            message_controllers.send_message(_get_message_json(form))
            survey = request.form.get("hidden_survey")
            flash("Message sent.")
            return redirect(url_for('messages_bp.view_selected_survey', selected_survey=survey))
        except (ApiError, InternalError):
            form = _repopulate_form_with_submitted_data(form)
            form.errors['sending'] = ["Message failed to send, something has gone wrong with the website."]
            return render_template('create-message.html',
                                   form=form,
                                   breadcrumbs=breadcrumbs)

    return render_template('create-message.html',
                           form=form,
                           breadcrumbs=breadcrumbs)


@messages_bp.route('/threads/<thread_id>', methods=['GET', 'POST'])
@login_required
def view_conversation(thread_id):
    try:
        thread_conversation = message_controllers.get_conversation(thread_id)['messages']
        refined_thread = [_refine(message) for message in reversed(thread_conversation)]
        breadcrumbs = _get_conversation_breadcrumbs(thread_conversation)
    except KeyError as e:
        logger.exception("A key error occurred")
        raise ApiError(e)
    except IndexError:
        breadcrumbs = [
            {"title": "Messages", "link": "/messages"},
            {"title": "Unavailable"}
        ]

    if refined_thread[-1]['unread']:
        message_controllers.remove_unread_label(refined_thread[-1]['message_id'])

    form = SecureMessageForm(request.form)

    if form.validate_on_submit():
        form = _populate_form_details_from_hidden_fields(form)
        g.form_subject_data = form.subject.data
        g.form_body_data = form.body.data

        try:
            message_controllers.send_message(
                _get_message_json(form,
                                  thread_id=refined_thread[0]['thread_id'])
            )
            thread_url = url_for("messages_bp.view_conversation", thread_id=thread_id) + "#latest-message"
            flash(Markup(f'Message sent. <a href={thread_url}>View Message</a>'))
            return redirect(url_for('messages_bp.view_selected_survey', selected_survey=refined_thread[0]['survey']))
        except (ApiError, InternalError):
            form = _repopulate_form_with_submitted_data(form)
            form.errors['sending'] = ["Message failed to send, something has gone wrong with the website."]
            return render_template('conversation-view.html',
                                   form=form,
                                   breadcrumbs=breadcrumbs,
                                   messages=refined_thread,
                                   error="Message send failed")

    return render_template("conversation-view.html",
                           breadcrumbs=breadcrumbs,
                           messages=refined_thread,
                           form=form)


@messages_bp.route('/', methods=['GET'])
@login_required
def view_select_survey():
    try:
        selected_survey = session["messages_survey_selection"]
    except KeyError:
        return redirect(url_for("messages_bp.select_survey"))

    return redirect(url_for("messages_bp.view_selected_survey",
                            selected_survey=selected_survey))


@messages_bp.route('/select-survey', methods=['GET', 'POST'])
@login_required
def select_survey():
    breadcrumbs = [{"title": "Messages", "link": "/messages"},
                   {"title": "Filter by survey"}]
    survey_list = [survey.value for survey in Surveys]

    if request.method == 'POST':
        selected_survey = request.form.get('radio-answer')
        if selected_survey:
            return redirect(url_for("messages_bp.view_selected_survey",
                                    selected_survey=selected_survey))
        else:
            response_error = True
    else:
        response_error = False

    return render_template("message_select_survey.html",
                           breadcrumbs=breadcrumbs,
                           selected_survey=None,
                           response_error=response_error,
                           survey_list=survey_list)


@messages_bp.route('/<selected_survey>', methods=['GET'])
@login_required
def view_selected_survey(selected_survey):
    formatted_survey = format_short_name(selected_survey)
    session['messages_survey_selection'] = selected_survey
    breadcrumbs = [{"title": formatted_survey + " Messages"}]
    try:
        if selected_survey == Surveys.FDI.value:
            survey_id = _get_FDI_survey_id()
        else:
            survey_id = _get_survey_id(selected_survey)

        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')

        limit = request.args.get(get_parameter('limit'), type=int, default=5)

        params = {
            'survey': survey_id,
            'page': page,
            'limit': limit
        }

        count = message_controllers.get_conversation_count({'survey': survey_id})
        messages = [_refine(message) for message in message_controllers.get_thread_list(params)]

        pagination = get_pagination(page=page,
                                    per_page=per_page,
                                    total=count,
                                    record_name='messages',
                                    format_total=True,
                                    format_number=True)

        return render_template("messages.html", page=page, per_page=per_page,
                               breadcrumbs=breadcrumbs,
                               messages=messages[offset:offset + limit],
                               selected_survey=formatted_survey,
                               pagination=pagination,
                               change_survey=True)

    except TypeError:
        logger.exception("Failed to retrieve survey id")
        return render_template("messages.html",
                               breadcrumbs=breadcrumbs,
                               response_error=True)
    except NoMessagesError:
        logger.exception("Failed to retrieve messages")
        return render_template("messages.html",
                               breadcrumbs=breadcrumbs,
                               response_error=True)


def _build_create_message_breadcrumbs():
    return [
        {"title": "Messages", "link": "/messages"},
        {"title": "Create Message"}
    ]


def _get_conversation_breadcrumbs(messages):
    return [
        {"title": "Messages", "link": "/messages"},
        {"title": messages[-1].get('subject', 'No Subject')}
    ]


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(show_single_page=False, **kwargs)


def _repopulate_form_with_submitted_data(form):
    form.survey.text = form.hidden_survey.data
    form.ru_ref.text = form.hidden_ru_ref.data
    form.business.text = form.hidden_business.data
    form.to.text = form.hidden_to.data
    form.body.data = g.form_body_data
    form.subject.data = g.form_subject_data
    return form


def _get_message_json(form, thread_id=""):
    return json.dumps({
        'msg_from': current_user.id,
        'msg_to': [form.hidden_to_uuid.data],
        'subject': form.subject.data,
        'body': form.body.data,
        'thread_id': thread_id,
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


def _get_message_subject(thread):
    try:
        subject = thread["subject"]
        return subject
    except KeyError:
        logger.exception("Failed to retrieve Subject from thread")
        return None


def _refine(message):
    return {
        'thread_id': message.get('thread_id'),
        'subject': _get_message_subject(message),
        'body': message.get('body'),
        'internal': message.get('from_internal'),
        'username': _get_user_summary_for_message(message),
        'survey_ref': get_survey_ref_by_id(message.get('survey')),
        'survey': get_survey_short_name_by_id(message.get('survey')),
        'survey_id': message.get('survey'),
        'ru_ref': _get_ru_ref_from_message(message),
        'to_id': _get_to_id(message),
        'from_id': message.get('msg_from'),
        'business_name': _get_business_name_from_message(message),
        'from': _get_from_name(message),
        'to': _get_to_name(message),
        'sent_date': _get_human_readable_date(message.get('sent_date')),
        'unread': _get_unread_status(message),
        'message_id': message.get('msg_id'),
        'ru_id': message.get('ru_id'),
    }


def _get_survey_id(selected_survey):
    return [survey_controllers.get_survey_id_by_short_name(selected_survey)]


def _get_FDI_survey_id():
    return [survey_controllers.get_survey_id_by_short_name(fdi_survey.value) for fdi_survey in FDISurveys]


def _get_user_summary_for_message(message):
    if message.get('from_internal'):
        return _get_from_name(message)
    return f'{_get_from_name(message)} - {_get_ru_ref_from_message(message)}'


def _get_from_name(message):
    try:
        msg_from = message['@msg_from']
        return f"{msg_from.get('firstName')} {msg_from.get('lastName')}"
    except KeyError:
        logger.exception("Failed to retrieve message from name", message_id=message.get('msg_id'))


def _get_to_id(message):
    try:
        return message.get('msg_to')[0]
    except (IndexError, TypeError):
        logger.exception("No 'msg_to' in message.", message_id=message.get('msg_id'))


def _get_to_name(message):
    try:
        if message.get('msg_to')[0] == 'GROUP':
            if get_survey_short_name_by_id(message.get('survey')):
                return f"{get_survey_short_name_by_id(message.get('survey'))} Team"
            return "ONS"
        return f"{message.get('@msg_to')[0].get('firstName')} {message.get('@msg_to')[0].get('lastName')}"
    except (IndexError, TypeError):
        logger.exception("Failed to retrieve message to name ", message_id=message.get('msg_id'))


def _get_ru_ref_from_message(message):
    try:
        return message['@ru_id']['sampleUnitRef']
    except (KeyError, TypeError):
        logger.exception("Failed to retrieve RU ref from message", message_id=message.get('msg_id'))


def _get_business_name_from_message(message):
    try:
        return message['@ru_id']['name']
    except (KeyError, TypeError):
        logger.exception("Failed to retrieve business name from message", message_id=message.get('msg_id'))


def _get_human_readable_date(sent_date):
    try:
        formatted_date = get_formatted_date(sent_date.split('.')[0])
        return formatted_date
    except (AttributeError, ValueError, IndexError, TypeError):
        logger.exception("Failed to parse sent date from message", sent_date=sent_date)


def _get_unread_status(message):
    return 'UNREAD' in message.get('labels', [])
