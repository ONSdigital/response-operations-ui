from flask import (
    Blueprint,
    flash,
    get_flashed_messages,
    make_response,
    redirect,
    session,
    url_for,
)
from flask_login import logout_user

logout_bp = Blueprint("logout_bp", __name__, static_folder="static", template_folder="templates")


@logout_bp.route("/")
def logout():
    logout_user()
    flashed_messages = get_flashed_messages(with_categories=True)
    session.clear()
    if len(flashed_messages) > 0:
        for category, message in flashed_messages:
            flash(message=message, category=category)
    else:
        flash("You are now signed out", category="successful_signout")

    response = make_response(redirect(url_for("sign_in_bp.sign_in")))
    return response
