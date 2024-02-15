import logging

from flask import Blueprint, render_template, request, url_for
from flask_login import login_required
from structlog import wrap_logger
from werkzeug.utils import redirect

from response_operations_ui.common.dates import get_formatted_date
from response_operations_ui.common.mappers import (
    format_short_name,
    map_ce_response_status,
)
from response_operations_ui.contexts.case import build_response_status_context
from response_operations_ui.controllers import (
    case_controller,
    collection_exercise_controllers,
    party_controller,
    survey_controllers,
)
from response_operations_ui.controllers.case_controller import (
    get_case_by_case_group_id,
    get_case_events_by_case_id,
)
from response_operations_ui.controllers.party_controller import (
    get_respondent_by_party_id,
)
from response_operations_ui.controllers.uaa_controller import user_has_permission
from response_operations_ui.forms import ChangeGroupStatusForm

ALLOWED_TRANSITIONS = ["COMPLETEDBYPHONE", "NOLONGERREQUIRED", "NOTSTARTED"]
COMPLETE_STATE = ["COMPLETE"]
COMPLETED_CASE_EVENTS = ["OFFLINE_RESPONSE_PROCESSED", "SUCCESSFUL_RESPONSE_UPLOAD", "COMPLETED_BY_PHONE"]
SUCCESSFUL_CASE_EVENTS = ["OFFLINE_RESPONSE_PROCESSED", "SUCCESSFUL_RESPONSE_UPLOAD", "ONLINE_QUESTIONNAIRE_RESPONSE"]
case_bp = Blueprint("case_bp", __name__, static_folder="static", template_folder="templates")

logger = wrap_logger(logging.getLogger(__name__))


@case_bp.route("/<ru_ref>/response-status", methods=["GET"])
@login_required
def get_response_statuses(ru_ref, error=None):
    logger.info("Retrieving response statuses", ru_ref=ru_ref)
    short_name = request.args.get("survey")
    period = request.args.get("period")

    completed_respondent = ""

    survey = survey_controllers.get_survey_by_shortname(short_name)

    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey["id"])
    exercise = collection_exercise_controllers.get_collection_exercise_from_list(exercises, period)

    reporting_unit = party_controller.get_business_by_ru_ref(ru_ref)

    possible_transitions_for_case = case_controller.get_available_case_group_statuses_direct(exercise["id"], ru_ref)

    case_groups = case_controller.get_case_groups_by_business_party_id(reporting_unit["id"])
    case_group = case_controller.get_case_group_by_collection_exercise(case_groups, exercise["id"])
    case_group_status = case_group["caseGroupStatus"]
    case_id = get_case_by_case_group_id(case_group["id"]).get("id")
    is_case_complete = case_group_status in COMPLETE_STATE
    completed_timestamp = get_timestamp_for_completed_case_event(case_id) if is_case_complete else None

    if is_case_complete:
        case_events = get_case_events_by_case_id(case_id=case_id)
        case_event = get_case_event_for_seft_or_eq(case_events)
        completed_respondent = get_user_from_case_events(case_event)

    # Using a list filter to return only the status we actually require. This is then used
    # to create the dictionary with only the required allowed transitions for certain case events
    allowed_transitions_filtered = list(filter(lambda statuses: statuses != case_group_status, ALLOWED_TRANSITIONS))

    allowed_transitions_for_case = {
        event: map_ce_response_status(status)
        for event, status in possible_transitions_for_case.items()
        if status in allowed_transitions_filtered
    }

    has_reporting_unit_permission = user_has_permission("reportingunits.edit")
    context = build_response_status_context(
        ru_ref,
        format_short_name(survey["shortName"]),
        case_group["id"],
        period,
        allowed_transitions_for_case,
        survey["id"],
        has_reporting_unit_permission,
    )

    return render_template(
        "response-status.html",
        ru_ref=ru_ref,
        ru_name=reporting_unit["name"],
        trading_as=reporting_unit["trading_as"],
        survey_short_name=format_short_name(survey["shortName"]),
        survey_ref=survey["surveyRef"],
        survey_id=survey["id"],
        ce_period=period,
        allowed_transitions_for_case=allowed_transitions_for_case,
        case_group_status=map_ce_response_status(case_group_status),
        case_group_id=case_group["id"],
        error=error,
        is_case_complete=is_case_complete,
        completed_timestamp=completed_timestamp,
        completed_respondent=completed_respondent,
        context=context,
    )


@case_bp.route("/<ru_ref>/response-status", methods=["POST"])
@login_required
def update_response_status(ru_ref):
    short_name = request.args.get("survey")
    period = request.args.get("period")
    case_group_id = request.args["case_group_id"]
    form = ChangeGroupStatusForm(request.form)

    if not form.event.data:
        return redirect(
            url_for(
                "case_bp.get_response_statuses",
                ru_ref=ru_ref,
                survey=short_name,
                period=period,
                error="Please select one of these options",
            )
        )

    # Retrieve the correct collection exercise and update case group status
    case = case_controller.get_case_by_case_group_id(case_group_id)
    case_controller.post_case_event(case["id"], form.event.data, "Transition case group status")

    return redirect(url_for("reporting_unit_bp.view_reporting_unit", ru_ref=ru_ref, survey=short_name, period=period))


def get_timestamp_for_completed_case_event(case_id):
    case_events = get_case_events_by_case_id(case_id, COMPLETED_CASE_EVENTS)
    last_index = len(case_events) - 1
    timestamp = case_events[last_index]["createdDateTime"].replace("T", " ").split(".")[0]

    return get_formatted_date(timestamp)


def get_case_event_for_seft_or_eq(case_events):
    case_event = [event for event in case_events if event["category"] in SUCCESSFUL_CASE_EVENTS]
    return case_event


def get_user_from_case_events(case_events):
    first_case_event = len(case_events) - 1
    if case_events[first_case_event]["metadata"]:
        try:
            respondent = get_respondent_by_party_id(case_events[first_case_event]["metadata"]["partyId"])
        except KeyError:
            logger.info("There was no partyId in case event", case_event=case_events[first_case_event])
            return ""
        if not respondent:
            return "Respondent does not exists in the system. This may be due to the GDPR retention policy."
        return respondent.get("firstName") + " " + respondent.get("lastName")
    else:
        return ""
