import logging
import requests
import json

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_user
from structlog import wrap_logger

from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User
from response_operations_ui import app

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
        url = f'{app.config["BACKSTAGE_API_URL"]}/sign-in-uaa'

        response = requests.post(url, json=sign_in_data)
        response_json = json.loads(response.text)

        if 'token' in response_json:
            user = User(response_json['token'])
            login_user(user)

            next_url = request.args.get('next')

            # Do we test if the redirect is safe or just assume it's fine?
            return redirect(next_url or url_for('home_bp.home'))
        else:
            form.username.errors.append(response_json['error'])

    logger.info(form.errors)
    return render_template('sign_in.html', form=form)
