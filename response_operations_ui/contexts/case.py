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
    case_completed_time: datetime = None,
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
            "radios_section": _generate_radios_section(
                allowed_transitions_for_case, case_completed_time, ru_ref, survey_id
            ),
        }
    else:
        change_response_status = {}
    return {"change_response_status": change_response_status}


def _generate_radios_section(
    allowed_transitions_for_case: dict, case_completed_time: datetime, ru_ref: str, survey_id: str
) -> dict:
    radios = []
    enabled_radios_button = True
    for index, (event, status) in enumerate(allowed_transitions_for_case.items()):
        radio = {"id": f"state-{index + 1}", "label": {"text": status}, "value": event}
        if event == "COMPLETED_TO_NOTSTARTED" and case_completed_time:
            enabled_radios_button = False
            complete_to_not_started_wait_time = app.config["COMPLETE_TO_NOT_STARTED_WAIT_TIME"]
            if (datetime.now() - case_completed_time) < timedelta(seconds=complete_to_not_started_wait_time):
                radio["attributes"] = {"disabled": "true"}
                radio["label"][
                    "description"
                ] = "Status can only be changed after 48 hours have passed since the submission"
            else:
                enabled_radios_button = True
        radios.append(radio)

    return {
        "radios": radios,
        "confirm_button_variant": None if enabled_radios_button else "disabled",
        "cancel_link": url_for("reporting_unit_bp.view_reporting_unit_survey", ru_ref=ru_ref, survey_id=survey_id),
    }
