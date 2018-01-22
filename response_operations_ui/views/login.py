import logging

from flask import Blueprint, render_template, request
from flask_login import login_user
from structlog import wrap_logger

from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User

logger = wrap_logger(logging.getLogger(__name__))

login_bp = Blueprint('login_bp', __name__, static_folder='static', template_folder='templates/sign-in')


@login_bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        # username = request.form.get('username')
        # password = request.form.get('password')
        # sign_in_data = {
        #     "username": "username",
        #     "password": "password"
        # }

        # For now log in the user without checking
        # response = api_call('POST', 'sign-in', json=sign_in_data)

        user = User(request.form.get('username'))
        login_user(user)

    return render_template('sign-in.html', form=form)
