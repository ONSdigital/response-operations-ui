import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

messages_bp = Blueprint("messages_bp", __name__, static_folder='Static',
                        template_folder='/templates/messages')

@messages_bp.route('/', methods=['GET'])
@login_required
def view_messages():
    message_list = {"subject": "subject text",
                   "ru_id": "12345ab",
                   "from": "person",
                   "to": "other person",
                   "received": "01/01/2018T00:00:00"}

    breadcrumbs = [{"title": "Messages"}]
    return render_template("messages.html", breadcrumbs=breadcrumbs, message_list=message_list)