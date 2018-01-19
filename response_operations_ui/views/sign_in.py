import logging

from flask import Blueprint, render_template, request
from structlog import wrap_logger

from response_operations_ui.models import LoginForm

logger = wrap_logger(logging.getLogger(__name__))

sign_in_bp = Blueprint('sign_in_bp', __name__, static_folder='static', template_folder='templates/sign-in')


@sign_in_bp.route('/')
def my_form():
    return render_template('sign-in.html')


@sign_in_bp.route('/', methods=['POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        sign_in_data = {
            "username": username,
            "password": password
        }

        response = api_call('POST', 'sign-in', json=sign_in_data)

    return render_template('sign-in.html')
