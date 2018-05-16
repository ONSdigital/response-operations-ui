from flask import Blueprint, flash, redirect, session, url_for
from flask_login import logout_user


logout_bp = Blueprint('logout_bp', __name__, static_folder='static', template_folder='templates')


@logout_bp.route('/')
def logout():
    logout_user()
    session.clear()
    flash("You are now signed out", category='successful_signout')
    return redirect(url_for('sign_in_bp.sign_in'))
