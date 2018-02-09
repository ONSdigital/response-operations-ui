import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import message_controllers

logger = wrap_logger(logging.getLogger(__name__))

messages_bp = Blueprint("messages_bp", __name__, static_folder='Static',
                        template_folder='templates')


@messages_bp.route('/', methods=['GET'])
@login_required
def view_messages():
    # TODO: Accept an optional label parameter so this endpoint can be used for inbox/drafts/sent

    # TODO: Aceept an optional survey name parameter to this get so that the inbox isn't every message ever sent by
    # an internal person. We'll need to figure out how to get the survey_id that secure-message service
    # will require.  Maybe call the rm-survey-service for all the id's of the surveys in the environement
    # and save it within the app?
    messages = message_controllers.get_message_list()
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
