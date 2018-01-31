import logging

from flask import Blueprint, redirect, render_template, request, url_for, session
from flask_login import login_user
from structlog import wrap_logger

from response_operations_ui.controllers import sign_in_controller
from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User

logger = wrap_logger(logging.getLogger(__name__))

sign_in_bp = Blueprint('sign_in_bp', __name__, static_folder='static', template_folder='templates')


@sign_in_bp.route('/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        sign_in_data = {
            "username": request.form.get('username'),
            "password": request.form.get('password'),
        }

        response_json = sign_in_controller.sign_in(sign_in_data)

        if 'token' in response_json:
            user = User(response_json['token'])
            login_user(user)
            if 'next' in session:
                return redirect(session['next'])
            else:
                return redirect(url_for('home_bp.home'))

    return render_template('sign_in.html', form=form)
