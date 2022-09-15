import json
import logging

from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, logout_user
from itsdangerous import BadData, BadSignature, SignatureExpired
from structlog import wrap_logger

from response_operations_ui.common import dates, token_decoder
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import NotifyError
from response_operations_ui.forms import (
    ChangeAccountName,
    ChangeEmailForm,
    ChangePasswordFrom,
    MyAccountOptionsForm,
    SetAccountPasswordForm,
)

logger = wrap_logger(logging.getLogger(__name__))

account_bp = Blueprint("account_bp", __name__, static_folder="static", template_folder="templates")

form_redirect_mapper = {
    "change_name": "account_bp.change_account_name",
    "change_email": "account_bp.change_email",
    "change_password": "account_bp.change_password",
}


@account_bp.route("/my-account", methods=["GET", "POST"])
@login_required
def get_my_account():
    form = MyAccountOptionsForm()
    if request.method == "POST":
        form_valid = form.validate()
        if form_valid:
            return redirect(url_for(form_redirect_mapper.get(form.data["option"])))
        flash("You need to choose an option")
    user_id = session["user_id"]
    user_from_uaa = uaa_controller.get_user_by_id(user_id)
    first_name = user_from_uaa["name"]["givenName"]
    last_name = user_from_uaa["name"]["familyName"]
    formatted_date = dates.format_datetime_to_string(user_from_uaa["passwordLastModified"], date_format="%d %b %Y")
    user = {
        "username": user_from_uaa["userName"],
        "name": f"{first_name} {last_name}",
        "email": user_from_uaa["emails"][0]["value"],
        "password_last_changed": formatted_date,
    }
    return render_template("account/my-account.html", user=user)


@account_bp.route("/change-account-name", methods=["GET", "POST"])
@login_required
def change_account_name():
    form = ChangeAccountName()
    user_id = session["user_id"]
    user_from_uaa = uaa_controller.get_user_by_id(user_id)
    user = {
        "first_name": f"{user_from_uaa['name']['givenName']}",
        "last_name": f"{user_from_uaa['name']['familyName']}",
    }
    if request.method == "POST" and form.validate():
        if (form.data["first_name"] != user["first_name"]) or (form.data["last_name"] != user["last_name"]):
            user_from_uaa["name"] = {"familyName": form.data["last_name"], "givenName": form.data["first_name"]}
            full_name = f"{form.data['first_name']} {form.data['last_name']}"
            logger.info("Sending update account details email", user_id=user_id)
            personalisation = {
                "first_name": user["first_name"],
                "value_name": "name",
                "changed_value": full_name,
            }
            try:
                NotifyController().request_to_notify(
                    email=user_from_uaa["emails"][0]["value"],
                    template_name="update_account_details",
                    personalisation=personalisation,
                )
                errors = uaa_controller.update_user_account(user_from_uaa)
                if errors is None:
                    flash("Your name has been changed", category="successful_signout")
                    return redirect(url_for("logout_bp.logout"))
                else:
                    logger.error("Error changing user information", msg=errors)
                    flash(
                        "Something went wrong. Please ignore the email you have received and try again",
                        category="error",
                    )
            except NotifyError as e:
                logger.error("Error sending change of name acknowledgement email to Notify Gateway", msg=e.description)
                flash("Something went wrong while updating your name. Please try again", category="error")
        else:
            return redirect(url_for("account_bp.get_my_account"))
    return render_template("account/change-account-name.html", user=user, form=form, errors=form.errors)


@account_bp.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    form = ChangeEmailForm()

    if request.method == "POST" and form.validate():
        user_id = session["user_id"]
        uaa_user = uaa_controller.get_user_by_id(user_id)

        if uaa_user is None:
            return render_template("request-new-account-error.html")

        current_email = uaa_user["emails"][0]["value"]
        new_email = form.data["email_address"]

        if current_email != new_email and _can_change_username_and_email(new_email):
            first_name = uaa_user["name"]["givenName"]

            if _notify_account_update_emails_sent(current_email, new_email, first_name, user_id):
                flash(
                    "A verification email has been sent.",
                    category="successful_signout",
                )
                return redirect(url_for("logout_bp.logout"))

            flash("Something went wrong while updating your email. Please try again", category="error")
        else:
            logger.info(f"Unable to change username and email for {user_id}, email already used")
            flash("Email already in use", category="error")

    return render_template("account/change-email.html", form=form, errors=form.errors)


def _notify_account_update_emails_sent(current_email: str, new_email: str, first_name: str, user_id: str) -> bool:
    notify_controller = NotifyController()

    update_account_details_personalisation = {
        "first_name": first_name,
        "value_name": "email",
        "changed_value": new_email,
    }
    token = token_decoder.generate_token(json.dumps({"email": new_email, "user_id": user_id}))
    verification_url = f"{app.config['RESPONSE_OPERATIONS_UI_URL']}/account/verify-email/{token}"
    update_email_personalisation = {"CONFIRM_EMAIL_URL": verification_url, "first_name": first_name}
    logger.info("Sending update account verification email", verification_url=verification_url)

    try:
        notify_controller.request_to_notify(
            email=new_email, template_name="update_email", personalisation=update_email_personalisation
        )
        notify_controller.request_to_notify(
            email=current_email,
            template_name="update_account_details",
            personalisation=update_account_details_personalisation,
        )
    except NotifyError as e:
        logger.error(
            f"Error sending change of email acknowledgement to Notify Gateway for {user_id}", msg=e.description
        )
        return False

    return True


def _can_change_username_and_email(new_email: str) -> bool:
    user_filter = f"email+eq+%22{new_email}%22+or+userName+eq+%22{new_email}%22"
    uaa_user = uaa_controller.get_user_by_filter(user_filter)

    if uaa_user and uaa_user["totalResults"] == 0:
        return True

    return False


@account_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    try:
        duration = app.config["UPDATE_ACCOUNT_EMAIL_TOKEN_EXPIRY"]
        json_token = token_decoder.decode_email_token(token, duration)
        token_dict = json.loads(json_token)

        user_from_uaa = uaa_controller.get_user_by_id(token_dict["user_id"])

        if user_from_uaa is None:
            return render_template("request-new-account-error.html")

        user_from_uaa["emails"][0]["value"] = token_dict["email"]
        user_from_uaa["userName"] = token_dict["email"]

        errors = uaa_controller.update_user_account(user_from_uaa)

        if errors is not None:
            logger.error("Error updating email and username in UAA", msg=errors["message"])
            flash("Failed to update email. Please try again", category="warn")
        else:
            flash("Your email has been changed", category="successful_signout")
            return redirect(url_for("account_bp.confirm_email_change"))

        return redirect(url_for("logout_bp.logout"))
    except SignatureExpired:
        logger.warning("Token expired for Response Operations email change", token=token)
        flash("Your link has expired", category="successful_signout")
        return redirect(url_for("logout_bp.logout"))
    except (BadSignature, BadData):
        logger.warning("Invalid token sent to Response Operations email change", token=token)
        flash("Your link is invalid", category="successful_signout")
        return redirect(url_for("logout_bp.logout"))


@account_bp.route("/confirm-email-change", methods=["GET"])
def confirm_email_change():
    logout_user()
    session.clear()
    return render_template("account/confirm-email-change.html")


@account_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordFrom()
    user_id = session["user_id"]
    user_from_uaa = uaa_controller.get_user_by_id(user_id)
    if request.method == "POST" and form.validate():
        password = form["password"].data
        new_password = form["new_password"].data
        if new_password == password:
            return render_template(
                "account/change-password.html",
                form=form,
                errors={"new_password": ["Your new password is the same as your old password"]},
            )
        personalisation = {"first_name": user_from_uaa["name"]["givenName"]}
        uaa_errors = uaa_controller.update_user_password(user_from_uaa, password, new_password)
        if uaa_errors is None:
            logger.info("Sending account password acknowledgement email", user_id=user_id)
            try:
                NotifyController().request_to_notify(
                    email=user_from_uaa["emails"][0]["value"],  # Safe to assume that zeroth element is primary email
                    template_name="update_account_password",
                    personalisation=personalisation,
                )
            except NotifyError as e:
                logger.error(
                    "Error sending change of password acknowledgement email to Notify Gateway", msg=e.description
                )
                flash("We were unable to send the password change acknowledgement email.", category="warn")
            flash("Your password has been changed", category="successful_signout")
            return redirect(url_for("logout_bp.logout"))
        else:
            logger.error("Error changing user password", msg=uaa_errors)
            if uaa_errors["status_code"] == 401:
                flash(
                    "your current password is incorrect. Please re-enter a correct current password.",
                    category="error",
                )
            else:
                flash(
                    "Something went wrong while updating your password. Please try again.",
                    category="error",
                )
    return render_template("account/change-password.html", form=form, errors=form.errors)


@account_bp.route("/activate-account/<token>", methods=["GET"])
def get_activate_account(token):
    duration = app.config["CREATE_ACCOUNT_EMAIL_TOKEN_EXPIRY"]
    user_id = token_decoder.decode_email_token(token, duration)
    user = uaa_controller.get_user_by_id(user_id)
    if user is None:
        raise Exception("User does not exist")
    form = SetAccountPasswordForm()
    return render_template("account/activate-account.html", form=form, username=user["userName"])


@account_bp.route("/activate-account/<token>", methods=["POST"])
def post_activate_account(token):
    duration = app.config["CREATE_ACCOUNT_EMAIL_TOKEN_EXPIRY"]
    user_id = token_decoder.decode_email_token(token, duration)
    user = uaa_controller.get_user_by_id(user_id)
    if user is None:
        raise Exception("User does not exist")
    form = SetAccountPasswordForm(request.form)

    if not form.validate():
        return render_template("account/activate-account.html", form=form, username=user["userName"])

    result = uaa_controller.change_user_password_by_id(user_id, form.password.data)
    if result is None:
        flash("Something went wrong setting password and activating account, please try again", "error")
        return render_template("account/activate-account.html", form=form, username=user["userName"])

    flash("Account successfully activated", category="account_created")
    return redirect(url_for("sign_in_bp.sign_in"))


def send_confirm_created_email(email, first_name):
    personalisation = {"FIRST_NAME": first_name}

    try:
        NotifyController().request_to_notify(
            email=email, template_name="confirm_create_account", personalisation=personalisation
        )
    except NotifyError as e:
        # This shouldn't show the client an error - the account creation was still successful.
        # They just won't get a confirmation email
        logger.error("Error sending account creation confirmation email to Notify Gateway", msg=e.description)
