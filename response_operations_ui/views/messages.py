import json
import logging
from urllib.parse import parse_qs

from flask import Blueprint, render_template, request, redirect, url_for, g
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import message_controllers
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.forms import SecureMessageForm

logger = wrap_logger(logging.getLogger(__name__))
messages_bp = Blueprint('messages_bp', __name__,
                        static_folder='static', template_folder='templates')


@messages_bp.route('/create-message', methods=['GET', 'POST'])
@login_required
def create_message():
    form = SecureMessageForm(request.form)
    breadcrumbs = [
        {
            "title": "Messages",
            "link": "/messages"
        },
        {
            "title": "Create Message"
        }
    ]

    if form.validate_on_submit():
        # TODO logic for sending message and confirmation on redirect and controller

        # Hard coded id's until we can fetch them from UAA or passed by Reporting Units page
        message_json = json.dumps({
            'msg_from': "BRES",
            'msg_to': ["f62dfda8-73b0-4e0e-97cf-1b06327a6712"],
            'subject': form.subject.data,
            'body': form.body.data,
            'thread_id': "",
            'collection_case': "CC_PLACEHOLDER",
            'survey': form.hidden_survey.data,
            'ru_id': "c614e64e-d981-4eba-b016-d9822f09a4fb"})

        # Keep the message subject and body
        g.form_subject_data = form.subject.data
        g.form_body_data = form.body.data

        try:
            message_controllers.send_message(message_json)

        except ApiError:

            form.survey.text = form.hidden_survey.data
            form.ru_ref.text = form.hidden_ru_ref.data
            form.business.text = form.hidden_business.data
            form.to.text = form.hidden_to.data
            form.body.data = g.form_body_data
            form.subject.data = g.form_subject_data

            form.errors['sending'] = ["Something went wrong: Message failed to send"]

            return render_template('create-message.html',
                                   _theme='default',
                                   form=form,
                                   breadcrumbs=breadcrumbs)
        return redirect(url_for('messages_bp.view_messages'))

    else:
        if not form.is_submitted():
            query_ru = request.args.get('ru_details')
            ru_dict = parse_qs(query_ru)
            form.hidden_survey.data = ru_dict.get('survey')[0]
            form.hidden_ru_ref.data = ru_dict.get('ru_ref')[0]
            form.hidden_business.data = ru_dict.get('business')[0]
            form.hidden_to.data = ru_dict.get('to')[0]
            form.hidden_to_uuid.data = ru_dict.get('to_uuid')[0]
            form.hidden_to_ru_id.data = ru_dict.get('to_ru_id')[0]

        form.survey.text = form.hidden_survey.data
        form.ru_ref.text = form.hidden_ru_ref.data
        form.business.text = form.hidden_business.data
        form.to.text = form.hidden_to.data

        return render_template('create-message.html',
                               _theme='default',
                               form=form,
                               breadcrumbs=breadcrumbs)


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
    messages = message_controllers.get_message_list(params)
    refined_messages = [_refine(msg) for msg in messages]
    breadcrumbs = [{"title": "Messages"}]
    return render_template("messages.html", breadcrumbs=breadcrumbs, messages=refined_messages)


def _refine(message):
    return {
        'ru_ref': message.get('ru_id'),
        'business_name': message.get('@ru_id').get('name'),
        'subject': message.get('subject'),
        'from': message.get('msg_from'),
        'to': message.get('@msg_to')[0].get('firstName') + ' ' + message.get('@msg_to')[0].get('lastName'),
        'sent_date': message.get('sent_date')
    }
