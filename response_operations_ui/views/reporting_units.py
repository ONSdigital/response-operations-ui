import logging
from datetime import datetime, timezone

from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_paginate import Pagination
from iso8601 import parse_date
from structlog import wrap_logger

from response_operations_ui.common.mappers import map_ce_response_status, map_region
from response_operations_ui.controllers import (
    case_controller,
    iac_controller,
    party_controller,
    reporting_units_controllers,
    respondent_controllers,
)
from response_operations_ui.controllers.collection_exercise_controllers import (
    get_case_group_status_by_collection_exercise,
    get_collection_exercise_by_id,
)
from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.forms import EditContactDetailsForm, RuSearchForm

logger = wrap_logger(logging.getLogger(__name__))

reporting_unit_bp = Blueprint("reporting_unit_bp", __name__, static_folder="static", template_folder="templates")


@reporting_unit_bp.route("/<ru_ref>", methods=["GET"])
@login_required
def view_reporting_unit(ru_ref):
    logger.info("Gathering data to view reporting unit", ru_ref=ru_ref)
    # Make some initial calls to retrieve some data we'll need
    reporting_unit = party_controller.get_business_by_ru_ref(ru_ref)

    cases = case_controller.get_cases_by_business_party_id(
        reporting_unit["id"], app.config["MAX_CASES_RETRIEVED_PER_SURVEY"]
    )
    case_groups = [case["caseGroup"] for case in cases]

    # Get all collection exercises for retrieved case groups
    collection_exercise_ids = {case_group["collectionExerciseId"] for case_group in case_groups}
    collection_exercises = [get_collection_exercise_by_id(ce_id) for ce_id in collection_exercise_ids]
    live_collection_exercises = [
        ce for ce in collection_exercises if parse_date(ce["scheduledStartDateTime"]) < datetime.now(timezone.utc)
    ]

    survey_table_data = build_survey_table_data_dict(live_collection_exercises, case_groups)

    breadcrumbs = create_reporting_unit_breadcrumbs(ru_ref)

    logger.info("Successfully gathered data to view reporting unit", ru_ref=ru_ref)
    return render_template("reporting-unit.html", ru=reporting_unit, surveys=survey_table_data, breadcrumbs=breadcrumbs)


def build_survey_table_data_dict(collection_exercises: list, case_groups: list) -> list:
    """
    Creates the dictionary of survey & CE information for the front-end table to display

    :param collection_exercises: A list of collection exercises to add to the table
    :param case_groups: A list of case groups for the reporting unit
    :return: A sorted list of survey/CE information to provide to the front-end table
    """
    table_data = {}
    surveys = {}
    for ce in collection_exercises:
        # Keep a mini cache of surveys, so we don't have to keep asking for the same survey data repeatedly
        survey = surveys.get(ce["surveyId"])
        if survey is None:
            survey = get_survey_by_id(ce["surveyId"])
            surveys[ce["surveyId"]] = survey

        if survey["surveyRef"] in table_data:
            # Keep the one with the later go-live date
            if parse_date(table_data[survey["surveyRef"]]["goLive"]) > parse_date(ce["scheduledStartDateTime"]):
                continue
        table_data[survey["surveyRef"]] = {
            "surveyName": f"{survey['surveyRef']} {survey['shortName']}",
            "surveyId": ce["surveyId"],
            "shortName": survey["shortName"],
            "period": ce["exerciseRef"],
            "goLive": ce["scheduledStartDateTime"],
            "caseStatus": map_ce_response_status(get_case_group_status_by_collection_exercise(case_groups, ce["id"])),
        }
    return sorted(table_data.items(), key=lambda t: t[0])


@reporting_unit_bp.route("/<ru_ref>/respondents", methods=["GET"])
@login_required
def view_respondents(ru_ref: str):
    logger.info("Gathering data to view reporting unit respondents", ru_ref=ru_ref)
    # Make some initial calls to retrieve some data we'll need
    reporting_unit = party_controller.get_business_by_ru_ref(ru_ref)

    # Get all respondents for the given ru
    respondent_party_ids = [respondent["partyId"] for respondent in reporting_unit.get("associations")]
    respondents = party_controller.get_respondent_by_party_ids(respondent_party_ids)

    respondent_table_data = build_respondent_table_data_dict(respondents, ru_ref)

    breadcrumbs = create_reporting_unit_breadcrumbs(ru_ref)
    logger.info("Successfully gathered data to view reporting unit respondents", ru_ref=ru_ref)

    return render_template(
        "reporting-unit-respondents.html", ru=reporting_unit, respondents=respondent_table_data, breadcrumbs=breadcrumbs
    )


def build_respondent_table_data_dict(respondents: list, ru_ref: str):
    table_data = {}
    survey_data = {}
    for respondent in respondents:
        table_data[respondent["id"]] = {
            "respondent": f"{respondent['firstName']} {respondent['lastName']}",
            "status": respondent["status"].title(),
            "surveys": {},
            "id": respondent["id"],
        }
        respondent_surveys = party_controller.survey_ids_for_respondent(respondent, ru_ref)
        for survey_id in respondent_surveys:
            # Build up a cache of survey ref/name pairs
            if survey_id not in survey_data:
                survey = get_survey_by_id(survey_id)
                survey_data[survey_id] = f"{survey['surveyRef']} {survey['shortName']}"

            enrolment_status = next(
                iter(party_controller.add_enrolment_status_for_respondent(respondent, ru_ref, survey_id))
            )
            table_data[respondent["id"]]["surveys"][survey_id] = {
                "name": survey_data[survey_id],
                "status": enrolment_status,
            }

        table_data[respondent["id"]]["surveys"] = sorted(
            table_data[respondent["id"]]["surveys"].items(), key=lambda t: t[1]["name"]
        )

    return sorted(table_data.values(), key=lambda t: t["respondent"])


@reporting_unit_bp.route("/<ru_ref>/surveys/<survey_id>", methods=["GET"])
@login_required
def view_reporting_unit_survey(ru_ref, survey_id):
    logger.info("Gathering data to view reporting unit survey data", ru_ref=ru_ref, survey_id=survey_id)
    # Make some initial calls to retrieve some data we'll need
    reporting_unit = party_controller.get_business_by_ru_ref(ru_ref)
    max_number_of_cases = request.args.get("max-number-of-cases", app.config["MAX_CASES_RETRIEVED_PER_SURVEY"])
    if int(max_number_of_cases) == 0:
        flash("Maximum number of cases cannot be 0.  Using default maximum instead", "error")
        max_number_of_cases = app.config["MAX_CASES_RETRIEVED_PER_SURVEY"]
    cases = case_controller.get_cases_by_business_party_id(reporting_unit["id"], max_number_of_cases)
    case_groups = [case["caseGroup"] for case in cases]

    # Get all collection exercises for retrieved case groups and only for the survey we care about.
    collection_exercise_ids = {
        case_group["collectionExerciseId"] for case_group in case_groups if case_group["surveyId"] == survey_id
    }
    collection_exercises = [get_collection_exercise_by_id(ce_id) for ce_id in collection_exercise_ids]
    live_collection_exercises = [
        ce for ce in collection_exercises if parse_date(ce["scheduledStartDateTime"]) < datetime.now(timezone.utc)
    ]

    # Get all respondents for the given ru
    respondent_party_ids = [respondent["partyId"] for respondent in reporting_unit.get("associations")]
    respondents = party_controller.get_respondent_by_party_ids(respondent_party_ids)

    survey_respondents = [
        party_controller.add_enrolment_status_for_respondent(respondent, ru_ref, survey_id)
        for respondent in respondents
        if survey_id in party_controller.survey_ids_for_respondent(respondent, ru_ref)
    ]

    survey_collection_exercises = sorted(
        [collection_exercise for collection_exercise in live_collection_exercises],
        key=lambda ce: ce["scheduledStartDateTime"],
        reverse=True,
    )

    attributes = party_controller.get_business_attributes_by_party_id(reporting_unit["id"])
    collection_exercises_with_details = [
        add_collection_exercise_details(ce, attributes[ce["id"]], case_groups) for ce in survey_collection_exercises
    ]

    survey_details = get_survey_by_id(survey_id)
    survey_details["display_name"] = f"{survey_details['surveyRef']} {survey_details['shortName']}"

    # If there's an active IAC on the newest case, return it to be displayed
    live_collection_exercise_ids = [ce["id"] for ce in survey_collection_exercises]
    valid_cases = [
        case for case in cases if case.get("caseGroup", {}).get("collectionExerciseId") in live_collection_exercise_ids
    ]
    case = next(iter(sorted(valid_cases, key=lambda c: c["createdDateTime"], reverse=True)), None)
    unused_iac = ""
    if case is not None and iac_controller.is_iac_active(case["iac"]):
        unused_iac = case["iac"]

    logger.info("Successfully gathered data to view reporting unit survey data", ru_ref=ru_ref, survey_id=survey_id)

    return render_template(
        "reporting-unit-survey.html",
        ru=reporting_unit,
        survey=survey_details,
        respondents=survey_respondents,
        collection_exercises=collection_exercises_with_details,
        iac=unused_iac,
        case=case,
    )


def add_collection_exercise_details(collection_exercise, reporting_unit, case_groups):
    collection_exercise["responseStatus"] = map_ce_response_status(
        get_case_group_status_by_collection_exercise(case_groups, collection_exercise["id"])
    )
    collection_exercise["companyName"] = reporting_unit["name"]
    collection_exercise["companyRegion"] = map_region(reporting_unit["attributes"]["region"])
    collection_exercise["tradingAs"] = reporting_unit["trading_as"]

    return collection_exercise


@reporting_unit_bp.route("/<ru_ref>/edit-contact-details/<respondent_id>", methods=["GET"])
@login_required
def view_contact_details(ru_ref, respondent_id):
    respondent_details = party_controller.get_respondent_by_party_id(respondent_id)

    form = EditContactDetailsForm(form=request.form, default_values=respondent_details)

    return render_template(
        "edit-contact-details.html",
        ru_ref=ru_ref,
        respondent_details=respondent_details,
        form=form,
        tab="reporting_units",
    )


@reporting_unit_bp.route("/<ru_ref>/edit-contact-details/<respondent_id>", methods=["POST"])
@login_required
def edit_contact_details(ru_ref, respondent_id):
    edit_contact_details_form = EditContactDetailsForm(form=request.form)
    if not edit_contact_details_form.validate():
        contact_details = party_controller.get_respondent_by_party_id(respondent_id)

        return render_template(
            "edit-contact-details.html",
            form=edit_contact_details_form,
            tab="reporting_units",
            ru_ref=ru_ref,
            respondent_id=respondent_id,
            errors=edit_contact_details_form.errors,
            respondent_details=contact_details,
        )

    logger.info("Updating respondent details", ru_ref=ru_ref, respondent_id=respondent_id)
    form = request.form
    contact_details_changed = party_controller.update_contact_details(respondent_id, form, ru_ref)

    if "emailAddress" in contact_details_changed:
        flash(f'Contact details changed and verification email sent to {form.get("email")}')
    elif len(contact_details_changed) > 0:
        flash("Contact details changed")
    else:
        flash("No updates were necessary")

    return redirect(url_for("reporting_unit_bp.view_reporting_unit", ru_ref=ru_ref))


@reporting_unit_bp.route("/", methods=["GET"])
@login_required
def search_reporting_unit_home():
    return render_template(
        "reporting-unit-search/reporting-units-search.html",
        form=RuSearchForm(),
        breadcrumbs=[{"text": "Reporting units"}],
    )


@reporting_unit_bp.route("/", methods=["POST"])
@login_required
def search_redirect():
    form = RuSearchForm(request.form)

    if form.validate_on_submit():
        query = request.form.get("query")

        return redirect(url_for("reporting_unit_bp.search_reporting_units", query=query))


@reporting_unit_bp.route("/search", methods=["GET"])
@login_required
def search_reporting_units():
    search_key_words = request.values.get("query", "")
    page = request.values.get("page", "1")
    limit = app.config["PARTY_BUSINESS_RESULTS_PER_PAGE"]
    max_rec = app.config["PARTY_BUSINESS_RESULTS_TOTAL"]
    breadcrumbs = [{"text": "Reporting units"}]
    form = RuSearchForm()
    form.query.data = search_key_words
    # this tells us if the search is all numbers
    # if yes we take it as ru search and not keyword search
    is_ru_search = search_key_words.isdecimal()

    response_data = reporting_units_controllers.search_reporting_units(search_key_words, limit, page, is_ru_search)

    business_list = response_data["businesses"]
    total_business_count = response_data["total_business_count"]

    offset = (int(page) - 1) * limit
    last_index = (limit + offset) if total_business_count >= limit else total_business_count

    pagination = Pagination(
        page=int(page),
        per_page=limit,
        total=len(business_list) if len(business_list) != 0 and total_business_count <= limit else total_business_count,
        record_name="Business",
        prev_label="Previous",
        next_label="Next",
        outer_window=0,
        format_total=True,
        format_number=True,
        show_single_page=False,
    )

    return render_template(
        "reporting-unit-search/reporting-units.html",
        form=form,
        business_list=business_list,
        total_business_count=len(business_list)
        if len(business_list) != 0 and total_business_count <= limit
        else total_business_count,
        breadcrumbs=breadcrumbs,
        first_index=1 + offset,
        last_index=last_index,
        pagination=pagination,
        show_pagination=bool(total_business_count > limit) and total_business_count < max_rec,
        max_rec=max_rec,
    )


# Not sure why is this endpoint exposed : Amit Sinha
@reporting_unit_bp.route("/resend_verification/<ru_ref>/<party_id>", methods=["GET"])
@login_required
def view_resend_verification(ru_ref, party_id):
    logger.info("Re-send verification email requested", ru_ref=ru_ref, party_id=party_id)
    respondent = party_controller.get_respondent_by_party_id(party_id)
    email = respondent["pendingEmailAddress"] if "pendingEmailAddress" in respondent else respondent["emailAddress"]

    return render_template("re-send-verification-email.html", ru_ref=ru_ref, email=email, tab="reporting_units")


# Not sure why is this endpoint exposed : Amit Sinha
@reporting_unit_bp.route("/resend_verification/<ru_ref>/<party_id>", methods=["POST"])
@login_required
def resend_verification(ru_ref, party_id):
    form = request.form
    is_new_account_verification = True if form.get("change") == "new-account-email" else False
    respondent_controllers.resend_verification_email(party_id, is_new_account_verification)
    logger.info("Re-sent verification email.", party_id=party_id)
    flash("Verification email re-sent")
    return redirect(url_for("reporting_unit_bp.view_reporting_unit", ru_ref=ru_ref))


@reporting_unit_bp.route("/<ru_ref>/new_enrolment_code", methods=["GET"])
@login_required
def generate_new_enrolment_code(ru_ref):
    case_id = request.args.get("case_id")
    reporting_units_controllers.generate_new_enrolment_code(case_id)
    case = case_controller.get_case_by_id(case_id)
    return render_template(
        "new-enrolment-code.html",
        iac=case["iac"],
        ru_ref=ru_ref,
        ru_name=request.args.get("ru_name"),
        trading_as=request.args.get("trading_as"),
        survey_name=request.args.get("survey_name"),
        survey_ref=request.args.get("survey_ref"),
    )


@reporting_unit_bp.route("/<ru_ref>/change-enrolment-status", methods=["GET"])
@login_required
def confirm_change_enrolment_status(ru_ref):
    return render_template(
        "confirm-enrolment-change.html",
        business_id=request.args["business_id"],
        ru_ref=ru_ref,
        ru_name=request.args.get("ru_name"),
        trading_as=request.args["trading_as"],
        survey_id=request.args["survey_id"],
        survey_name=request.args["survey_name"],
        respondent_id=request.args["respondent_id"],
        first_name=request.args["respondent_first_name"],
        last_name=request.args["respondent_last_name"],
        change_flag=request.args["change_flag"],
        tab=request.args["tab"],
    )


@reporting_unit_bp.route("/<ru_ref>/change-respondent-status", methods=["GET"])
@login_required
def confirm_change_respondent_status(ru_ref):
    respondent = party_controller.get_respondent_by_party_id(request.args["party_id"])
    return render_template(
        "confirm-respondent-status-change.html",
        ru_ref=ru_ref,
        respondent_id=respondent["id"],
        first_name=respondent["firstName"],
        last_name=respondent["lastName"],
        email_address=respondent["emailAddress"],
        change_flag=request.args["change_flag"],
        tab=request.args["tab"],
    )


@reporting_unit_bp.route("/<ru_ref>/change-enrolment-status", methods=["POST"])
@login_required
def change_enrolment_status(ru_ref):
    reporting_units_controllers.change_enrolment_status(
        business_id=request.args["business_id"],
        respondent_id=request.args["respondent_id"],
        survey_id=request.args["survey_id"],
        change_flag=request.args["change_flag"],
    )
    return redirect(url_for("reporting_unit_bp.view_reporting_unit", ru_ref=ru_ref, enrolment_changed="True"))


@reporting_unit_bp.route("/<ru_ref>/change-respondent-status", methods=["POST"])
@login_required
def change_respondent_status(ru_ref):
    reporting_units_controllers.change_respondent_status(
        respondent_id=request.args["respondent_id"], change_flag=request.args["change_flag"]
    )
    return redirect(url_for("reporting_unit_bp.view_reporting_unit", ru_ref=ru_ref, account_status_changed="True"))


def create_reporting_unit_breadcrumbs(ru_ref: str) -> list:
    return [{"text": "Reporting units", "url": "/reporting-units"}, {"text": f"{ru_ref}"}]
