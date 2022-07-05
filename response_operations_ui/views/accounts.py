import json
import logging

from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, logout_user
from itsdangerous import BadData, BadSignature, SignatureExpired, URLSafeSerializer
from structlog import wrap_logger

from response_operations_ui.common import dates, token_decoder
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.controllers.respondent_controllers import obfuscate_email
from response_operations_ui.exceptions.exceptions import NotifyError
from response_operations_ui.forms import (
    ChangeAccountName,
    ChangeEmailForm,
    ChangePasswordFrom,
    CreateAccountForm,
    MyAccountOptionsForm,
    RequestAccountForm,
    UsernameChangeForm,
    VerifyAccountForm,
)

logger = wrap_logger(logging.getLogger(__name__))

account_bp = Blueprint("account_bp", __name__, static_folder="static", template_folder="templates")

form_redirect_mapper = {
    "change_name": "account_bp.change_account_name",
    "change_username": "account_bp.change_username",
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
    url_safe_serializer = URLSafeSerializer(app.config["SECRET_KEY"])
    form = ChangeEmailForm()
    user_id = session["user_id"]
    user_from_uaa = uaa_controller.get_user_by_id(user_id)
    if request.method == "POST" and form.validate():
        if form.data["email_address"] != user_from_uaa["emails"][0]["value"]:
            personalisation = {
                "first_name": user_from_uaa["name"]["givenName"],
                "value_name": "email",
                "changed_value": form.data["email_address"],
            }
            try:
                logger.info("Sending verification email", email=obfuscate_email(form.data["email_address"]))
                token_dict = {"email": form.data["email_address"], "user_id": user_id}
                send_update_account_email(token_dict, user_from_uaa["name"]["givenName"])
                logger.info("Sending notification email")
                NotifyController().request_to_notify(
                    email=user_from_uaa["emails"][0]["value"],
                    template_name="update_account_details",
                    personalisation=personalisation,
                )
                logger.info(
                    "Successfully sent email change email",
                    encoded_email=url_safe_serializer.dumps(form.data["email_address"]),
                )
                flash(
                    "A verification email has been sent. You will need to login to change your email",
                    category="successful_signout",
                )
                return redirect(url_for("logout_bp.logout"))
            except NotifyError as e:
                logger.error("Error sending 'email change' email to Notify Gateway", msg=e.description)
                flash("Something went wrong while updating your email. Please try again", category="error")
        else:
            return redirect(url_for("account_bp.get_my_account"))
    return render_template("account/change-email.html", form=form, errors=form.errors)


@account_bp.route("/verify-email/<token>", methods=["GET"])
@login_required
def verify_email(token):
    try:
        duration = app.config["UPDATE_ACCOUNT_EMAIL_TOKEN_EXPIRY"]
        json_token = token_decoder.decode_email_token(token, duration)
        token_dict = json.loads(json_token)
        user_id = session["user_id"]
        if token_dict["user_id"] == user_id:
            user_from_uaa = uaa_controller.get_user_by_id(user_id)
            user_from_uaa["emails"][0]["value"] = token_dict["email"]
            logger.info("Updating email in UAA")
            errors = uaa_controller.update_user_account(user_from_uaa)
            if errors is not None:
                logger.error("Error updating email in UAA", msg=errors["message"])
                flash("Failed to update email. Please try again", category="warn")
            else:
                flash("Your email has been changed", category="successful_signout")
                return redirect(url_for("account_bp.confirm_email_change"))
        else:
            logger.error("Invalid link for user", user_id=user_id)
            flash("Invalid link", category="warn")
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


@account_bp.route("/change-username", methods=["GET", "POST"])
@login_required
def change_username():
    form = UsernameChangeForm()
    user_id = session["user_id"]
    user_from_uaa = uaa_controller.get_user_by_id(user_id)
    username = user_from_uaa["userName"]
    username_exists = False
    if request.method == "POST" and form.validate():
        if form["username"].data != username:
            user_from_uaa["userName"] = form["username"].data
            logger.info("Sending update account details email", user_id=user_id)
            personalisation = {
                "first_name": user_from_uaa["name"]["givenName"],
                "value_name": "username",
                "changed_value": form["username"].data,
            }
            try:
                NotifyController().request_to_notify(
                    email=user_from_uaa["emails"][0]["value"],
                    template_name="update_account_details",
                    personalisation=personalisation,
                )
                uaa_errors = uaa_controller.update_user_account(user_from_uaa)
                if uaa_errors is None:
                    flash("Your username has been changed", category="successful_signout")
                    return redirect(url_for("logout_bp.logout"))
                elif uaa_errors["status_code"] == 400:
                    username_exists = True
                else:
                    logger.error("Error changing user information", msg=uaa_errors)
                    flash(
                        "Something went wrong. Please ignore the email you have received and try again",
                        category="error",
                    )
            except NotifyError as e:
                logger.error(
                    "Error sending change of username acknowledgement email to Notify Gateway", msg=e.description
                )
                flash("Something went wrong while updating your username. Please try again", category="error")
        else:
            return redirect(url_for("account_bp.get_my_account"))
    errors = form.errors
    if username_exists:
        errors = {"username": [uaa_errors["message"]]}
    return render_template("account/change-username.html", username=username, form=form, errors=errors)


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
        logger.info("Sending account password acknowledgement email", user_id=user_id)
        personalisation = {"first_name": user_from_uaa["name"]["givenName"]}
        uaa_errors = uaa_controller.update_user_password(user_from_uaa, password, new_password)
        if uaa_errors is None:
            try:
                NotifyController().request_to_notify(
                    email=user_from_uaa["emails"][0]["value"],  # it's safe to assume that zeroth element is primary in
                    # RAS/RM case
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
                    "Something went wrong while updating your username. Please try again.",
                    category="error",
                )
    errors = form.errors
    return render_template("account/change-password.html", form=form, errors=errors)


@account_bp.route("/request-new-account", methods=["GET"])
def get_request_new_account(form_errors=None, email=None):
    form = RequestAccountForm(request.form)
    template_data = {"error": {"type": form_errors}}
    return render_template("request-new-account.html", form=form, data=template_data, email=email)


@account_bp.route("/request-new-account", methods=["POST"])
def post_request_new_account():
    form = RequestAccountForm(request.form)
    form.email_address.data = form.email_address.data.strip()
    email = form.data.get("email_address")

    if form.validate():
        password = form.data.get("password")
        admin_password = app.config["CREATE_ACCOUNT_ADMIN_PASSWORD"]
        if password != admin_password:
            logger.info("Invalid password provided for create account")
            template_data = {"error": {"type": {"password": ["Incorrect admin secret"]}}}
            return render_template("request-new-account.html", form=form, data=template_data, email=email)

        return send_create_account_email(email)

    template_data = {"error": {"type": {"email_address": ["Not a valid ONS email address"]}}}
    return render_template("request-new-account.html", form=form, data=template_data, email=email)


def send_update_account_email(token_dict, first_name):
    """Sends an email through GovNotify to the specified address with an encoded
     link to verify their email when it has been changed

    :param token_dict: A dictionary containing the email address to send to and user id
    :param first_name: the name of the user the email is being sent to, used in email
    """
    response = uaa_controller.get_user_by_email(token_dict["email"])
    if response is None:
        return render_template("request-new-account-error.html")

    if response["totalResults"] == 0:
        internal_url = app.config["RESPONSE_OPERATIONS_UI_URL"]
        verification_url = (
            f"{internal_url}/account/verify-email/{token_decoder.generate_email_token(json.dumps(token_dict))}"
        )

        logger.info("Sending update account verification email", verification_url=verification_url)
        personalisation = {"CONFIRM_EMAIL_URL": verification_url, "first_name": first_name}
        NotifyController().request_to_notify(
            email=token_dict["email"], template_name="update_email", personalisation=personalisation
        )
    else:
        url_safe_serializer = URLSafeSerializer(app.config["SECRET_KEY"])
        logger.info(
            "Requested account creation for email already in UAA",
            encoded_email=url_safe_serializer.dumps(token_dict["email"]),
        )
        flash("Email already in use", category="error")


def send_create_account_email(email):
    """Sends an email through GovNotify to the specified address with an encoded link to verify their email

    :param email: The email address to send to
    """
    url_safe_serializer = URLSafeSerializer(app.config["SECRET_KEY"])

    response = uaa_controller.get_user_by_email(email)
    if response is None:
        return render_template("request-new-account-error.html")

    if response["totalResults"] == 0:
        internal_url = app.config["RESPONSE_OPERATIONS_UI_URL"]
        verification_url = f"{internal_url}/account/create-account/{token_decoder.generate_email_token(email)}"

        logger.info("Sending create account email", verification_url=verification_url)

        personalisation = {"CREATE_ACCOUNT_URL": verification_url, "EMAIL": email}

        try:
            NotifyController().request_to_notify(
                email=email, template_name="request_create_account", personalisation=personalisation
            )
        except NotifyError as e:
            logger.error("Error sending create account request email to Notify Gateway", msg=e.description)
            return render_template("request-new-account-error.html")

        logger.info("Successfully sent create account request email", encoded_email=url_safe_serializer.dumps(email))
    else:
        logger.info(
            "Requested account creation for email already in UAA", encoded_email=url_safe_serializer.dumps(email)
        )
        return render_template("request-new-account-exists.html", email=email)

    return render_template("request-new-account-check-email.html", email=email)


@account_bp.route("/resend_account_email_expired_token/<token>", methods=["GET"])
def resend_account_email_expired_token(token):
    email = token_decoder.decode_email_token(token)
    return send_create_account_email(email)


@account_bp.route("/create-account/<token>", methods=["GET"])
def get_create_account(token, form_errors=None):
    form = CreateAccountForm(request.form)

    try:
        duration = app.config["EMAIL_TOKEN_EXPIRY"]
        _ = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning("Token expired for Response Operations account creation", token=token)
        return render_template("request-new-account-expired.html", token=token)
    except (BadSignature, BadData):
        logger.warning("Invalid token sent to Response Operations account creation", token=token)
        return render_template("request-new-account-expired.html", token=token)

    template_data = {"error": {"type": form_errors}, "token": token}
    return render_template("create-new-account.html", form=form, data=template_data)


@account_bp.route("/create-account/<token>", methods=["POST"])
def post_create_account(token):
    form = CreateAccountForm(request.form)

    if not form.validate():
        template_data = {"error": {"type": form.errors}, "token": token}
        return render_template("create-new-account.html", form=form, data=template_data)

    try:
        duration = app.config["EMAIL_TOKEN_EXPIRY"]
        email = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning("Token expired for Response Operations create account", token=token)
        return render_template("request-new-account-expired.html", token=token)
    except (BadSignature, BadData):
        logger.warning("Invalid token sent to Response Operations create account", token=token)
        return render_template("request-new-account-expired.html", token=token)

    password = request.form.get("password")
    user_name = request.form.get("user_name")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    errors = uaa_controller.create_user_account(email, password, user_name, first_name, last_name)

    if errors is None:
        logger.info("Successfully created user account", token=token)
        send_confirm_created_email(email, first_name)
        flash("Account successfully created", category="account_created")
        return redirect(url_for("sign_in_bp.sign_in"))
    else:
        if "user_name" in errors:
            template_data = {"error": {"type": errors}, "token": token}
            return render_template("create-new-account.html", form=form, data=template_data)

        return render_template("create-new-account-error.html")


@account_bp.route("/verify-account/<token>", methods=["GET"])
def get_verify_account(token):
    form = VerifyAccountForm()
    return render_template("account/verify-account.html", form=form)


@account_bp.route("/verify-account/<token>", methods=["POST"])
def post_verify_account(token):
    form = VerifyAccountForm(request.form)
    # TODO decode token and get id from it
    user_id = token
    if not form.validate():
        return render_template("account/verify-account.html", form=form)

    uaa_controller.change_user_password_for_verify_journey(user_id, form.password.data)
    uaa_controller.verify_user(user_id)
    flash("Account successfully verified", category="account_created")
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
