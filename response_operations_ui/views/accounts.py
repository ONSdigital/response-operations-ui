import logging

from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from itsdangerous import BadData, BadSignature, SignatureExpired, URLSafeSerializer
from structlog import wrap_logger

from response_operations_ui.common import dates, token_decoder
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import NotifyError
from response_operations_ui.forms import (
    ChangeAccountName,
    CreateAccountForm,
    MyAccountOptionsForm,
    RequestAccountForm,
)

logger = wrap_logger(logging.getLogger(__name__))

account_bp = Blueprint("account_bp", __name__, static_folder="static", template_folder="templates")

form_redirect_mapper = {
    "change_name": "account_bp.change_account_name",
    "change_username": "account_bp.change_username",
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
    user_from_uaa["name"] = {"familyName": form.data["last_name"], "givenName": form.data["first_name"]}
    if request.method == "POST" and form.validate():
        if (form.data["first_name"] != user["first_name"]) or (form.data["last_name"] != user["last_name"]):
            errors = uaa_controller.update_user_account(user_from_uaa)
            if errors is None:
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
                    return redirect(url_for("logout_bp.logout", message="Your name has been changed"))
                except NotifyError as e:
                    logger.error(
                        "Error sending change of name acknowledgement email to Notify Gateway", msg=e.description
                    )
                    return redirect(
                        url_for(
                            "logout_bp.logout",
                            message="Your name has been changed however you may not receive an email",
                        )
                    )
        else:
            return redirect(url_for("account_bp.get_my_account"))
    return render_template("account/change-account-name.html", user=user, form=form, errors=form.errors)


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
