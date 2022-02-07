from flask import Blueprint, flash, make_response, redirect, request, session, url_for
from flask_login import logout_user

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
