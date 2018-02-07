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
    messages = message_controllers.get_message_list()
    breadcrumbs = [{"title": "Messages"}]
    return render_template("messages.html", breadcrumbs=breadcrumbs, messages=messages)
