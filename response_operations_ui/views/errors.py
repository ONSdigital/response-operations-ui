import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import (
    ApiError,
    RURetrievalError,
    UpdateContactDetailsException,
)

logger = wrap_logger(logging.getLogger(__name__))

error_bp = Blueprint("error_bp", __name__, template_folder="templates/errors")


@error_bp.app_errorhandler(ApiError)
def api_error(error):
    logger.error(
        error.message or "Api failed to retrieve required data",
        url=request.url,
        api_status_code=error.status_code,
        api_url=error.url,
    )
    return render_template("errors/500-error.html"), 500


@error_bp.app_errorhandler(UpdateContactDetailsException)
def update_details_exception(error=None):
    logger.error("update details error", ru_ref=error.ru_ref, status_code=error.status_code)
    error_type = "email conflict" if error.status_code == 409 else "api error"

    return render_template(
        "edit-contact-details.html",
        ru_ref=error.ru_ref,
        form=error.form,
        error_type=error_type,
        respondent_details=error.respondent_details,
    )


@error_bp.app_errorhandler(401)
def handle_authentication_error(error):
    logger.warning("Authentication failed")
    flash("Incorrect username or password", category="failed_authentication")
    return redirect(url_for("sign_in_bp.sign_in"))


@error_bp.app_errorhandler(Exception)
@error_bp.app_errorhandler(500)
def server_error(error):
    logger.exception("Generic exception generated", exc_info=error, url=request.url, status_code=500)
    return render_template("errors/500-error.html"), 500


@error_bp.app_errorhandler(RURetrievalError)
def ru_retrieval_error(error):
    logger.error(
        error.message,
        url=request.url,
        api_status_code=error.status_code,
        api_url=error.url,
    )
    return render_template(
        "errors/ru-error.html",
        ru_ref=error.ru_ref,
    )
