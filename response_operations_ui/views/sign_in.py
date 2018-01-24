import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_user
from structlog import wrap_logger

from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User

logger = wrap_logger(logging.getLogger(__name__))

sign_in_bp = Blueprint('sign_in_bp', __name__, static_folder='static', template_folder='templates/sign_in')


@sign_in_bp.route('/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(form.id.data)

        if username == 'user' and password == 'pass':
            login_user(user)

            next = request.args.get('next')

            return redirect(next or url_for('home_bp.home'))

    return render_template('sign_in.html', form=form)
