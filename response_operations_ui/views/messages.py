import logging
from urllib.parse import parse_qs

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.forms import SecureMessageForm

logger = wrap_logger(logging.getLogger(__name__))
messages_bp = Blueprint('messages_bp', __name__,
                        static_folder='static', template_folder='templates')


@messages_bp.route('/create-message', methods=['GET', 'POST'])
@login_required
def create_message():
    form = SecureMessageForm(request.form)
    if form.validate_on_submit():
        # TODO logic for sending message and confirmation on redirect and controller
        return redirect(url_for('home_bp.home'))

    else:
        if not form.is_submitted():
            query_ru = request.args.get('ru')
            ru_dict = parse_qs(query_ru)
            form.hidden_survey.data = ru_dict.get('survey')[0]
            form.hidden_ru_ref.data = ru_dict.get('ru_ref')[0]
            form.hidden_business.data = ru_dict.get('business')[0]
            form.hidden_to.data = ru_dict.get('to')[0]

        form.survey.text = form.hidden_survey.data
        form.ru_ref.text = form.hidden_ru_ref.data
        form.business.text = form.hidden_business.data
        form.to.text = form.hidden_to.data

        return render_template('create-message.html',
                               _theme='default',
                               form=form,
                               errors=form.errors)
