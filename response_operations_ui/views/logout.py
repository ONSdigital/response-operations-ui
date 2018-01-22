from flask import Blueprint, redirect, url_for
from flask_login import logout_user


logout_bp = Blueprint('logout_bp', __name__, static_folder='static', template_folder='templates')


@logout_bp.route('/')
def logout():
    logout_user()
    return redirect(url_for("login_bp.login"))
