import logging

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask import get_flashed_messages
from flask_login import current_user, login_user
from structlog import wrap_logger

from response_operations_ui.controllers import sign_in_controller
from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User

logger = wrap_logger(logging.getLogger(__name__))

sign_in_bp = Blueprint('sign_in_bp', __name__, static_folder='static', template_folder='templates')


@sign_in_bp.route('/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    if form.validate_on_submit():
        sign_in_data = {
            "username": request.form.get('username'),
            "password": request.form.get('password'),
        }

        response_json = sign_in_controller.sign_in(sign_in_data)

        try:
            # store the token in the session (it's server side and stored in redis)
            session['token'] = response_json['token']
            user = User(response_json.get('user_id'))
            login_user(user)
            if 'next' in session:
                return redirect(session['next'])
            return redirect(url_for('home_bp.home'))
        except KeyError:
            logger.exception("Token missing from authentication server response")

    for message in get_flashed_messages(with_categories=True):
        if "failed_authentication" in message:
            return render_template('sign_in.html', form=form, failed_authentication=True)

    return render_template('sign_in.html', form=form)
