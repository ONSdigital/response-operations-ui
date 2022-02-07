from flask import Blueprint, flash, redirect, url_for, request, make_response, session
from flask_login import logout_user
from response_operations_ui.common.session import Session

logout_bp = Blueprint("logout_bp", __name__, static_folder="static", template_folder="templates")


@logout_bp.route("/")
def logout():
    logout_user()
    session.clear()
    if request.args.get("message") is not None:
        flash(request.args.get("message"), category="successful_signout")
    else:
        flash("You are now signed out", category="successful_signout")
    response = make_response(redirect(url_for("sign_in_bp.sign_in")))
    return response
