import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_user
from structlog import wrap_logger

from response_operations_ui.controllers.sign_in_controller import get_sign_in
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

        response_json = get_sign_in(sign_in_data)

        if 'token' in response_json:
            user = User(response_json['token'])
            login_user(user)

            next_url = request.args.get('next')
            return redirect(next_url or url_for('home_bp.home'))
        else:
            form.username.errors.append(response_json['error'])

    return render_template('sign_in.html', form=form)
