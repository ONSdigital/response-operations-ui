import logging

from flask import (
    Blueprint,
    abort,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user
from jwt import DecodeError
from structlog import wrap_logger

from response_operations_ui.common import token_decoder
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.forms import LoginForm
from response_operations_ui.user import User

logger = wrap_logger(logging.getLogger(__name__))

sign_in_bp = Blueprint("sign_in_bp", __name__, static_folder="static", template_folder="templates")


@sign_in_bp.route("/", methods=["GET", "POST"])
def sign_in():
    form = LoginForm(request.form)
    if current_user.is_authenticated:
        return redirect(url_for("home_bp.home"))

    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")

        logger.info("Retrieving sign-in details")
        access_token = uaa_controller.sign_in(username, password)

        try:
            logger.info("Successfully retrieved sign-in details")
            token = token_decoder.decode_access_token(access_token)
            user_id = token.get("user_id")
        except DecodeError:
            logger.error("Unable to decode token - confirm the UAA public key is correct", access_token=access_token)
            abort(500)
        else:
            # store the token in the session (it's server side and stored in redis)
            session["token"] = access_token
            session["username"] = username
            session["user_id"] = user_id
            user = User(user_id, username)
            login_user(user)
            if "next" in session:
                return redirect(session["next"])
            return redirect(url_for("home_bp.home"))
    for message in get_flashed_messages(with_categories=True):
        if "failed_authentication" in message:
            return render_template(
                "sign_in.html",
                form=form,
                failed_authentication=True,
            )

    return render_template("sign_in.html", form=form)
