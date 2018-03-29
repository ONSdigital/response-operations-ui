from contextlib import suppress

from flask import Blueprint, flash, redirect, url_for, session
from flask_login import logout_user


logout_bp = Blueprint('logout_bp', __name__, static_folder='static', template_folder='templates')


@logout_bp.route('/')
def logout():
    logout_user()
    with suppress(KeyError):
        del session["message_survey"]
    flash("You are now signed out", category='successful_signout')
    return redirect(url_for('sign_in_bp.sign_in'))
