import json
import logging

from flask import Blueprint, flash, g, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from structlog import wrap_logger
import maya

from response_operations_ui.common.surveys import Surveys
from response_operations_ui.controllers import message_controllers, survey_controllers
from response_operations_ui.exceptions.exceptions import ApiError, InternalError, NoMessagesError
from response_operations_ui.forms import SecureMessageForm
from response_operations_ui.controllers.survey_controllers import get_survey_short_name_by_id

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
        refined_messages = [_refine(msg) for msg in message_controllers.get_thread_list(params)]
        return render_template("messages.html", breadcrumbs=breadcrumbs, messages=refined_messages)
    except NoMessagesError:
        return render_template("messages.html",
                               breadcrumbs=breadcrumbs,
                               response_error=True)


@messages_bp.route('/select-survey', methods=['GET', 'POST'])
@login_required
def view_select_survey():
    breadcrumbs = [{"title": "Messages", "link": "/messages"},
                   {"title": "Filter by survey"}]

    survey_list = [survey.value for survey in Surveys]

    if request.method == 'POST':
        selected_survey = request.form['radio-answer']
        return redirect(url_for("messages_bp.view_selected_survey",
                                selected_survey=selected_survey))
    else:
        return render_template("message_select_survey.html",
                               breadcrumbs=breadcrumbs,
                               survey_list=survey_list)


@messages_bp.route('/<selected_survey>', methods=['GET'])
@login_required
def view_selected_survey(selected_survey):
    breadcrumbs = [{"title": selected_survey + " Messages"}]

    params = {
        'label': request.args.get('label'),
        'survey': request.args.get('survey')
    }

    try:
        refined_messages = [_refine(message) for message in message_controllers.get_thread_list(params)]
        survey_id = _get_survey_id(selected_survey)

        filtered_messages = [messages for messages in refined_messages if messages['survey'] == survey_id]

        return render_template("messages.html",
                               breadcrumbs=breadcrumbs,
                               messages=filtered_messages,
                               selected_survey=selected_survey,
                               change_survey=True)

    except KeyError:
        logger.exception("Failed to retrieve survey id")
        return render_template("messages.html",
                               breadcrumbs=breadcrumbs,
                               response_error=True)
    except NoMessagesError:
        logger.exception("Failed to retrieve messages")
        return render_template("messages.html",
                               breadcrumbs=breadcrumbs,
                               response_error=True)


def _refine(message):
    return {
        'survey': message.get('survey'),
        'ru_ref': _get_ru_ref_from_message(message),
        'business_name': _get_business_name_from_message(message),
        'subject': message.get('subject'),
        'from': _get_from_name(message),
        'to': _get_to_name(message),
        'sent_date': _get_human_readable_date(message.get('sent_date'))
    }


def _get_survey_id(selected_survey):
    survey_messages = survey_controllers.get_survey(selected_survey)
    return survey_messages['survey']['id']


def _get_from_name(message):
    try:
        msg_from = message['@msg_from']
        return f"{msg_from.get('firstName')} {msg_from.get('lastName')}"
    except KeyError:
        logger.exception("Failed to retrieve message from name", message_id=message.get('msg_id'))


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
        slang_date = maya.parse(sent_date).slang_date().capitalize()
        sent_time = sent_date.split(' ')[1][0:5]
        return f'{slang_date} at {sent_time}'
    except (ValueError, IndexError, TypeError):
        logger.exception("Failed to parse sent date from message", sent_date=sent_date)
