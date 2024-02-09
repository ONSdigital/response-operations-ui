from flask import url_for


def build_case_context(
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    allowed_transitions_for_case,
    survey_id,
    has_reporting_unit_permission,
):
    change_response_status = _build_change_response_status(
        ru_ref,
        survey_short_name,
        case_group_id,
        ce_period,
        allowed_transitions_for_case,
        survey_id,
        has_reporting_unit_permission,
    )
    return {"change_response_status": change_response_status}


def _build_change_response_status(
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    allowed_transitions_for_case,
    survey_id,
    has_reporting_unit_permission,
):
    if has_reporting_unit_permission:
        change_response_status = {
            "form_action": url_for(
                "case_bp.update_response_status",
                ru_ref=ru_ref,
                survey=survey_short_name,
                case_group_id=case_group_id,
                period=ce_period,
            ),
            "radios": _generate_radios(allowed_transitions_for_case),
            "cancel_link": url_for("reporting_unit_bp.view_reporting_unit_survey", ru_ref=ru_ref, survey_id=survey_id),
        }
    else:
        change_response_status = {}
    return change_response_status


def _generate_radios(allowed_transitions_for_case):
    radios = []
    for index, (event, status) in enumerate(allowed_transitions_for_case.items()):
        radios.append({"id": f"state-{index + 1}", "label": {"text": status}, "value": event})
    return radios
