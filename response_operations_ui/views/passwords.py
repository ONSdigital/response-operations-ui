import logging

from flask import Blueprint, abort
from flask import current_app as app
from flask import redirect, render_template, request, url_for
from itsdangerous import BadData, BadSignature, SignatureExpired, URLSafeSerializer
from structlog import wrap_logger

from response_operations_ui.common import token_decoder
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import NotifyError
from response_operations_ui.forms import ForgotPasswordForm, SetAccountPasswordForm

logger = wrap_logger(logging.getLogger(__name__))

BAD_AUTH_ERROR = "Unauthorized user credentials"

passwords_bp = Blueprint("passwords_bp", __name__, static_folder="static", template_folder="templates")


@passwords_bp.route("/forgot-password", methods=["GET"])
def get_forgot_password():
    form = ForgotPasswordForm(request.form)
    return render_template("forgot-password.html", form=form)


@passwords_bp.route("/forgot-password", methods=["POST"])
def post_forgot_password():
    form = ForgotPasswordForm(request.form)
    form.email_address.data = form.email_address.data.strip()
    email = form.data.get("email_address")

    if form.validate():
        return send_password_change_email(email)

    return render_template("forgot-password.html", form=form, email=email)


@passwords_bp.route("/forgot-password/check-email", methods=["GET"])
def forgot_password_check_email():
    encoded_email = request.args.get("email")

    if encoded_email is None:
        logger.error("No email parameter supplied")
        return redirect(url_for("passwords_bp.get_forgot_password"))

    try:
        email = URLSafeSerializer(app.config["SECRET_KEY"]).loads(encoded_email)
        return render_template("forgot-password-check-email.html", email=email)
    except BadSignature:
        logger.error("Unable to decode email from URL", encoded_email=encoded_email)
        abort(404)


@passwords_bp.route("/reset-password/<token>", methods=["GET"])
def get_reset_password(token, form_errors=None):
    form = SetAccountPasswordForm(request.form)

    try:
        duration = app.config["EMAIL_TOKEN_EXPIRY"]
        _ = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning("Token expired for Response Operations password reset", token=token)
        return render_template("reset-password-expired.html", token=token)
    except (BadSignature, BadData):
        logger.warning("Invalid token sent to Response Operations password reset", token=token)
        return render_template("reset-password-expired.html", token=token)

    template_data = {"error": {"type": form_errors}, "token": token}
    return render_template("reset-password.html", form=form, data=template_data)


@passwords_bp.route("/reset-password/<token>", methods=["POST"])
def post_reset_password(token):
    form = SetAccountPasswordForm(request.form)

    if not form.validate():
        return get_reset_password(token, form_errors=form.errors)

    password = request.form.get("password")

    try:
        duration = app.config["EMAIL_TOKEN_EXPIRY"]
        email = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning("Token expired for Response Operations password reset", token=token)
        return render_template("reset-password-expired.html", token=token)
    except (BadSignature, BadData):
        logger.warning("Invalid token sent to Response Operations password reset", token=token)
        return render_template("reset-password-expired.html", token=token)

    response = uaa_controller.change_user_password_by_email(email, password)

    if response is not None:
        if response.status_code == 200:
            # 200 == All good
            logger.info("Successfully changed user password", token=token)
            send_confirm_change_email(email)
            return redirect(url_for("passwords_bp.reset_password_confirmation"))

        if response.status_code == 422:
            # 422 == New password same as old password
            logger.info("New password same as old password", token=token)
            errors = {"password": ["Please choose a different password or login with the old password"]}
            return get_reset_password(token, form_errors=errors)

    logger.warning("Error changing password in UAA", token=token)
    return render_template("reset-password-error.html")


@passwords_bp.route("/reset-password/confirmation", methods=["GET"])
def reset_password_confirmation():
    return render_template("reset-password-confirmation.html")


@passwords_bp.route("/resend-password-email-expired-token/<token>", methods=["GET"])
def resend_password_email_expired_token(token):
    email = token_decoder.decode_email_token(token)
    return send_password_change_email(email)


def send_password_change_email(email):
    url_safe_serializer = URLSafeSerializer(app.config["SECRET_KEY"])

    user_filter = f"email+eq+%22{email}%22"
    response = uaa_controller.get_user_by_filter(user_filter)
    if response is None:
        return render_template("forgot-password-error.html")

    if response["totalResults"] > 0:
        first_name = response["resources"][0]["name"]["givenName"]
        internal_url = app.config["RESPONSE_OPERATIONS_UI_URL"]
        verification_url = f"{internal_url}/passwords/reset-password/{token_decoder.generate_token(email)}"

        logger.info("Sending password change email", verification_url=verification_url)

        personalisation = {"RESET_PASSWORD_URL": verification_url, "FIRST_NAME": first_name}

        try:
            NotifyController().request_to_notify(
                email=email, template_name="request_password_change", personalisation=personalisation
            )
        except NotifyError as e:
            logger.error("Error sending password change request email to Notify Gateway", msg=e.description)
            return render_template("forgot-password-error.html")

        logger.info("Successfully sent password change request email", email=url_safe_serializer.dumps(email))
    else:
        # We still want to render the template for an email without an account to avoid
        # people fishing for valid emails
        logger.info("Requested password reset for email not in UAA", email=url_safe_serializer.dumps(email))

    return redirect(url_for("passwords_bp.forgot_password_check_email", email=url_safe_serializer.dumps(email)))


def send_confirm_change_email(email):
    user_filter = f"email+eq+%22{email}%22"
    user = uaa_controller.get_user_by_filter(user_filter)

    first_name = user["resources"][0]["name"]["givenName"]
    if first_name != "":
        personalisation = {"FIRST_NAME": first_name}

        try:
            NotifyController().request_to_notify(
                email=email, template_name="confirm_password_change", personalisation=personalisation
            )
        except NotifyError as e:
            # This shouldn't show the client an error - the password change was still successful.
            # They just won't get a confirmation email
            logger.error("Error sending password change confirmation email to Notify Gateway", msg=e.description)
