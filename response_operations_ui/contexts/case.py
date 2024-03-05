from datetime import datetime, timedelta

from flask import current_app as app
from flask import url_for


def build_response_status_context(
    ru_ref: str,
    survey_short_name: str,
    case_group_id: str,
    ce_period: str,
    allowed_transitions_for_case: dict,
    survey_id: str,
    has_reporting_unit_permission: bool,
    timestamp: datetime = None,
) -> dict:
    if has_reporting_unit_permission and allowed_transitions_for_case:
        change_response_status = {
            "url": url_for(
                "case_bp.update_response_status",
                ru_ref=ru_ref,
                survey=survey_short_name,
                case_group_id=case_group_id,
                period=ce_period,
            ),
            "radios": _generate_radios(allowed_transitions_for_case, timestamp),
            "cancel_link": url_for("reporting_unit_bp.view_reporting_unit_survey", ru_ref=ru_ref, survey_id=survey_id),
        }
    else:
        change_response_status = {}
    return {"change_response_status": change_response_status}


def _generate_radios(allowed_transitions_for_case: dict, timestamp: datetime) -> list:
    complete_to_not_started_wait_time = app.config["COMPLETE_TO_NOT_STARTED_WAIT_TIME"]
    radios = [
        {"id": f"state-{index + 1}", "label": {"text": status}, "value": event}
        for index, (event, status) in enumerate(allowed_transitions_for_case.items())
    ]
    if timestamp:
        for radio in radios:
            if (radio["value"] == "COMPLETED_TO_NOTSTARTED") and (
                (datetime.now() - timestamp) < timedelta(seconds=complete_to_not_started_wait_time)
            ):
                radio["attributes"] = {"disabled": "true"}
    return radios
