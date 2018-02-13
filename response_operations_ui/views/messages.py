import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import message_controllers
from response_operations_ui.exceptions.exceptions import NoMessages

logger = wrap_logger(logging.getLogger(__name__))

messages_bp = Blueprint("messages_bp", __name__, static_folder='Static',
                        template_folder='templates')


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
    except NoMessages:
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
