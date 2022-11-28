import logging
from datetime import datetime

from dateutil.tz import gettz
from flask import Blueprint, abort
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_paginate import Pagination
from iso8601 import ParseError, parse_date
from structlog import wrap_logger

from response_operations_ui.common.respondent_utils import filter_respondents
from response_operations_ui.controllers import (
    party_controller,
    reporting_units_controllers,
    respondent_controllers,
    survey_controllers,
)
from response_operations_ui.controllers.party_controller import (
    delete_pending_surveys_by_batch_number,
    resend_pending_surveys_email,
)
from response_operations_ui.controllers.uaa_controller import user_has_permission
from response_operations_ui.forms import EditContactDetailsForm, RespondentSearchForm

logger = wrap_logger(logging.getLogger(__name__))

respondent_bp = Blueprint("respondent_bp", __name__, static_folder="static", template_folder="templates")


@respondent_bp.route("/", methods=["GET"])
@login_required
def respondent_home():
    success_panel = request.args.get("success_panel")
    return render_template(
        "respondent-search/respondent-search.html",
        form=RespondentSearchForm(),
        breadcrumbs=[{"text": "Respondents"}, {}],
        success_panel=success_panel,
    )


@respondent_bp.route("/search", methods=["GET", "POST"])
@login_required
def search_redirect():
    form = RespondentSearchForm()
    form_valid = form.validate()

    if request.method == "POST":
        if not form_valid:
            flash("At least one input should be filled")
            return redirect(url_for("respondent_bp.respondent_home"))
        email_address = form.email_address.data or ""
        first_name = form.first_name.data or ""
        last_name = form.last_name.data or ""
    else:
        email_address = request.args.get("email", "")
        first_name = request.args.get("firstname", "")
        last_name = request.args.get("lastname", "")
    page = request.values.get("page", "1")

    pagination_href = "abcd"
    breadcrumbs = [{"text": "Respondents"}, {"text": "Search"}]

    limit = app.config["PARTY_RESPONDENTS_PER_PAGE"]

    party_response = party_controller.search_respondents(first_name, last_name, email_address, page, limit)

    respondents = party_response.get("data", [])
    total_respondents_available = party_response.get("total", 0)

    filtered_respondents = filter_respondents(respondents)

    results_per_page = app.config["PARTY_RESPONDENTS_PER_PAGE"]

    offset = (int(page) - 1) * results_per_page

    last_index = (
        (results_per_page + offset) if total_respondents_available >= results_per_page else total_respondents_available
    )

    pagination = Pagination(
        page=int(page),
        per_page=results_per_page,
        total=total_respondents_available,
        record_name="respondents",
        prev_label="Previous",
        next_label="Next",
        outer_window=0,
        format_total=True,
        format_number=True,
        show_single_page=False,
        href=pagination_href,
    )

    return render_template(
        "respondent-search/respondent-search-results.html",
        form=form,
        breadcrumb=breadcrumbs,
        respondents=filtered_respondents,
        respondent_count=total_respondents_available,
        first_index=1 + offset,
        last_index=last_index,
        pagination=pagination,
        show_pagination=bool(total_respondents_available > results_per_page),
    )


@respondent_bp.route("<respondent_id>/pending-surveys/<batch_number>", methods=["GET"])
@login_required
def confirm_delete_pending_surveys(respondent_id, batch_number):
    return render_template(
        "confirm-pending-surveys-delete.html",
        batch_number=batch_number,
        respondent_id=respondent_id,
        recipient_email=request.args["recipient_email"],
        is_transfer=request.args["is_transfer"],
    )


@respondent_bp.route("<respondent_id>/pending-surveys/<batch_number>", methods=["POST"])
@login_required
def delete_pending_surveys(respondent_id, batch_number):
    delete_pending_surveys_by_batch_number(batch_number)
    if request.args["is_transfer"] == "True":
        flash("You have successfully deleted the transfer request.")
    else:
        flash("You have successfully deleted the share request.")
    return redirect(url_for("respondent_bp.respondent_details", respondent_id=respondent_id))


@respondent_bp.route("<respondent_id>/pending-surveys/resend-email/<batch_number>", methods=["GET"])
@login_required
def send_pending_surveys_email(respondent_id, batch_number):
    response = resend_pending_surveys_email(batch_number)
    if response:
        flash(
            "You have successfully resent the [share/transfer] request email.", response["resend_pending_surveys_email"]
        )
    else:
        flash("Error resending the [share/transfer] request email.", "error")
    return redirect(url_for("respondent_bp.respondent_details", respondent_id=respondent_id))


@respondent_bp.route("/respondent-details/<respondent_id>", methods=["GET"])
@login_required
def respondent_details(respondent_id):
    respondent = party_controller.get_respondent_by_party_id(respondent_id)
    enrolments = party_controller.get_respondent_enrolments(respondent)
    account = respondent_controllers.find_respondent_account_by_username(respondent["emailAddress"])
    breadcrumbs = [{"text": "Respondents", "url": "/respondents"}, {"text": f"{respondent['emailAddress']}"}, {}]

    respondent["status"] = respondent["status"].title()

    info = request.args.get("info")
    if request.args.get("enrolment_changed"):
        flash("Enrolment status changed", "information")
    if request.args.get("account_status_changed"):
        flash("Account status changed", "information")
    elif info:
        flash(info, "information")

    # Share Surveys and Pending Surveys information collection section
    pending_surveys = party_controller.get_pending_surveys_by_party_id(respondent_id)
    pending_transfer_surveys = []
    pending_share_surveys = []
    for pending_survey in pending_surveys:
        if "is_transfer" in pending_survey and pending_survey["is_transfer"] is True:
            pending_transfer_surveys.append(pending_survey)
        else:
            pending_share_surveys.append(pending_survey)
    formatted_transfer_surveys = get_formatted_pending_surveys(pending_transfer_surveys)
    formatted_share_surveys = get_formatted_pending_surveys(pending_share_surveys)

    return render_template(
        "respondent.html",
        respondent=respondent,
        enrolments=enrolments,
        breadcrumbs=breadcrumbs,
        mark_for_deletion=account["mark_for_deletion"],
        pending_transfer_surveys=formatted_transfer_surveys,
        pending_share_surveys=formatted_share_surveys,
        respondent_id=respondent_id,
    )


def get_formatted_pending_surveys(pending_surveys: list) -> list:
    """
    Get formatted pending surveys related to the respondent
    :param pending_surveys: pending survey list to be formatted
    :type pending_surveys: list
    """
    formatted_pending_surveys = []
    if len(pending_surveys) > 0:
        distinct_batch_number = {pending_surveys["batch_no"] for pending_surveys in pending_surveys}
        for batch_number in distinct_batch_number:
            business_surveys_list = []
            distinct_businesses = set()
            for pending_survey in pending_surveys:
                if pending_survey["batch_no"] == batch_number:
                    distinct_businesses.add(pending_survey["business_id"])
                    recipient_email = pending_survey["email_address"]
                    time_shared = pending_survey["time_shared"]
            for business_id in distinct_businesses:
                business_surveys = []
                for pending_survey in pending_surveys:
                    if pending_survey["business_id"] == business_id and pending_survey["batch_no"] == batch_number:
                        business_surveys.append(
                            survey_controllers.get_survey_by_id(pending_survey["survey_id"]).get("shortName")
                        )
                selected_business = party_controller.get_business_by_party_id(business_id)
                business_surveys_list.append({"business_name": selected_business["name"], "surveys": business_surveys})
            formatted_pending_surveys.append(
                {
                    "batch_no": batch_number,
                    "recipient_email": recipient_email,
                    "time_shared": convert_events_to_new_format(time_shared),
                    "pending_survey_details": business_surveys_list,
                }
            )
    return formatted_pending_surveys


def convert_events_to_new_format(date: str) -> str:
    """
    This function formats time shared for pending shares

    :param: date in string format
    """
    try:
        date_time = parse_date(date)
    except ParseError:
        raise ParseError
    return ordinal_date_formatter("{S} %B %Y at %H:%M", date_time)


def suffix(day: int):
    """
    This function creates the ordinal suffix

    :param: day of the date time object
    :return: str ordinal suffix
    """
    return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def ordinal_date_formatter(date_format_required: str, date_to_be_formatted: datetime):
    """
    This function takes the required output format and date to be formatted and returns the ordinal date in required
    format.

    :param: date_format_required: output format in which date should be returned
    :param: date_to_be_formatted: the datetime object which needs ordinal date
    :return: str formatted date
    """
    # UTC/ BST adjustment
    date_to_be_formatted = date_to_be_formatted.astimezone(gettz("Europe/London"))
    return date_to_be_formatted.strftime(date_format_required).replace(
        "{S}", str(date_to_be_formatted.day) + suffix(date_to_be_formatted.day)
    )


@respondent_bp.route("/edit-contact-details/<respondent_id>", methods=["GET"])
@login_required
def view_contact_details(respondent_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    respondent_detail = party_controller.get_respondent_by_party_id(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_detail)

    return render_template(
        "edit-contact-details.html",
        respondent_details=respondent_detail,
        form=form,
        tab="respondents",
        respondent_id=respondent_id,
    )


@respondent_bp.route("/edit-contact-details/<respondent_id>", methods=["POST"])
@login_required
def edit_contact_details(respondent_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    edit_contact_details_form = EditContactDetailsForm(form=request.form)
    if not edit_contact_details_form.validate():
        contact_details = party_controller.get_respondent_by_party_id(respondent_id)

        return render_template(
            "edit-contact-details.html",
            form=edit_contact_details_form,
            tab="respondents",
            respondent_id=respondent_id,
            errors=edit_contact_details_form.errors,
            respondent_details=contact_details,
        )

    logger.info("Updating respondent details", respondent_id=respondent_id)
    form = request.form
    contact_details_changed = party_controller.update_contact_details(respondent_id, form)

    if "emailAddress" in contact_details_changed:
        flash(f'Contact details changed and verification email sent to {form.get("email")}')
    elif len(contact_details_changed) > 0:
        flash("Contact details changed")
    else:
        flash("No updates were necessary")

    return redirect(
        url_for("respondent_bp.respondent_details", respondent_id=respondent_id, message_key="details_changed")
    )


@respondent_bp.route("/resend-verification/<respondent_id>", methods=["GET"])
@login_required
def view_resend_verification(respondent_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    logger.info("Re-send verification email requested", respondent_id=respondent_id)
    respondent = party_controller.get_respondent_by_party_id(respondent_id)
    is_new_email_verification_request = True if "pendingEmailAddress" in respondent else False
    email = respondent["pendingEmailAddress"] if is_new_email_verification_request else respondent["emailAddress"]

    return render_template(
        "re-send-verification-email.html",
        respondent_id=respondent_id,
        email=email,
        tab="respondents",
        is_new_email_verification_request=is_new_email_verification_request,
    )


@respondent_bp.route("/resend-verification/<party_id>", methods=["POST"])
@login_required
def resend_verification(party_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    form = request.form
    is_new_account_verification = True if form.get("change") == "new-account-email" else False
    respondent_controllers.resend_verification_email(party_id, is_new_account_verification)
    logger.info("Re-sent verification email.", party_id=party_id)
    flash("Verification email re-sent")

    return redirect(
        url_for(
            "respondent_bp.respondent_details",
            respondent_id=party_id,
        )
    )


@respondent_bp.route("<respondent_id>/change-enrolment-status", methods=["POST"])
@login_required
def change_enrolment_status(respondent_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    reporting_units_controllers.change_enrolment_status(
        business_id=request.args["business_id"],
        respondent_id=respondent_id,
        survey_id=request.args["survey_id"],
        change_flag=request.args["change_flag"],
    )
    return redirect(url_for("respondent_bp.respondent_details", respondent_id=respondent_id, enrolment_changed="True"))


@respondent_bp.route("/<respondent_id>/change-respondent-status", methods=["POST"])
@login_required
def change_respondent_status(respondent_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    reporting_units_controllers.change_respondent_status(
        respondent_id=respondent_id, change_flag=request.args["change_flag"]
    )
    return redirect(
        url_for("respondent_bp.respondent_details", respondent_id=respondent_id, account_status_changed="True")
    )


@respondent_bp.route("/<party_id>/change-respondent-status", methods=["GET"])
@login_required
def confirm_change_respondent_status(party_id):
    if not user_has_permission("respondents.edit"):
        logger.exception("No respondent edit role")
        abort(401)
    respondent = party_controller.get_respondent_by_party_id(party_id)
    return render_template(
        "confirm-respondent-status-change.html",
        respondent_id=respondent["id"],
        first_name=respondent["firstName"],
        last_name=respondent["lastName"],
        email_address=respondent["emailAddress"],
        change_flag=request.args["change_flag"],
        tab="respondents",
    )


@respondent_bp.route("/delete-respondent/<respondent_id>", methods=["GET", "POST"])
@login_required
def delete_respondent(respondent_id):
    if not user_has_permission("respondents.delete"):
        logger.exception("No respondent delete role")
        abort(401)
    respondent = party_controller.get_respondent_by_party_id(respondent_id)

    if request.method == "POST":
        respondent_controllers.delete_respondent_account_by_username(respondent["emailAddress"])
        return redirect(
            url_for(
                "respondent_bp.respondent_home",
                success_panel="The account is pending deletion " "and will be deleted by the end the day.",
            )
        )
    breadcrumbs = [
        {"url": "/respondents", "text": "Respondents"},
        {"text": f"{respondent['emailAddress']}", "url": f"/respondents/respondent-details/{respondent_id}"},
        {},
    ]

    return render_template(
        "delete-respondent.html", respondent_details=respondent, delete=True, breadcrumbs=breadcrumbs
    )


@respondent_bp.route("/undo-delete-respondent/<respondent_id>", methods=["GET", "POST"])
@login_required
def undo_delete_respondent(respondent_id):
    if not user_has_permission("respondents.delete"):
        logger.exception("No respondent delete role")
        abort(401)
    respondent = party_controller.get_respondent_by_party_id(respondent_id)

    if request.method == "POST":
        respondent_controllers.undo_delete_respondent_account_by_username(respondent["emailAddress"])
        flash("The respondent’s account has been reactivated.", "success")
        return redirect(
            url_for(
                "respondent_bp.respondent_details",
                respondent_id=respondent_id,
            )
        )
    breadcrumbs = [
        {"url": "/respondents", "text": "Respondents"},
        {"text": f"{respondent['emailAddress']}", "url": f"/respondents/respondent-details/{respondent_id}"},
        {"text": "Cancel Delete"},
        {},
    ]
    return render_template(
        "delete-respondent.html", respondent_details=respondent, delete=False, breadcrumbs=breadcrumbs
    )
