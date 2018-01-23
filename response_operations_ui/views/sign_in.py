import logging

from flask import Blueprint, render_template, request
from flask_login import login_user
from structlog import wrap_logger

from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User

logger = wrap_logger(logging.getLogger(__name__))

sign_in_bp = Blueprint('sign_in_bp', __name__, static_folder='static', template_folder='templates/sign_in')


@sign_in_bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(form.id.data)

        if username == 'user' and password == 'pass':
            login_user(user)

            return render_template('home.html')

    return render_template('sign_in.html', form=form)
