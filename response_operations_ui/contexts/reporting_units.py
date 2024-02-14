from flask import url_for

CE_STATUS_CLASS = {
    "Not started": "ons-status--info",
    "In progress": "ons-status--pending",
    "Completed": "ons-status--success",
    "Completed by phone": "ons-status--success",
    "No longer required": "ons-status--dead",
}

ENROLMENT_ENABLED = "ENABLED"
ENROLMENT_PENDING = "PENDING"


def build_reporting_units_context(
    collection_exercises: list, ru: dict, survey: dict, respondents: list, case, unused_iac: str, permissions: dict
) -> dict:
    collection_exercise_section = _build_collection_exercise_section(
        collection_exercises, ru["sampleUnitRef"], survey["shortName"], permissions["reporting_unit_edit"]
    )
    respondents_section = _build_respondents_section(
        respondents,
        case["id"],
        collection_exercises[0]["id"],
        collection_exercises[0]["tradingAs"],
        ru["name"],
        ru["sampleUnitRef"],
        ru["id"],
        survey["surveyRef"],
        survey["shortName"],
        survey["id"],
        unused_iac,
        permissions,
    )

    return {"collection_exercise_section": collection_exercise_section, "respondents_section": respondents_section}


def _build_collection_exercise_section(
    collection_exercises: list, sample_unit_ref: str, survey_short_name: str, reporting_unit_permission: bool
) -> list:
    table = [
        {
            "status_class": (
                CE_STATUS_CLASS[ce["responseStatus"]]
                if ce["responseStatus"] in CE_STATUS_CLASS.keys()
                else "ons-status--error"
            ),
            "hyperlink": url_for(
                "case_bp.get_response_statuses",
                ru_ref=sample_unit_ref,
                survey=survey_short_name,
                period=ce["exerciseRef"],
            ),
            "hyperlink_text": "Change" if reporting_unit_permission else "View",
            "period": ce["exerciseRef"],
            "reporting_unit_name": ce["companyName"],
            "trading_as": ce["tradingAs"],
            "region": ce["companyRegion"],
            "response_status": ce["responseStatus"],
            "status": _build_ce_status(
                sample_unit_ref,
                survey_short_name,
                ce["exerciseRef"],
                ce["responseStatus"],
                reporting_unit_permission,
            ),
        }
        for ce in collection_exercises
    ]
    return table


def _build_ce_status(ru_ref: str, survey: str, period: str, response_status: str, ru_permission: bool) -> dict:
    ce_status = {
        "hyperlink": url_for(
            "case_bp.get_response_statuses",
            ru_ref=ru_ref,
            survey=survey,
            period=period,
        ),
        "hyperlink_text": "Change" if ru_permission else "View",
        "status_class": (
            CE_STATUS_CLASS[response_status] if response_status in CE_STATUS_CLASS.keys() else "ons-status--error"
        ),
        "response_status": response_status,
    }
    return ce_status


def _build_respondents_section(
    respondents: list,
    case_id: str,
    collection_exercise_id: str,
    trading_as: str,
    ru_name: str,
    sample_unit_ref: str,
    ru_id: str,
    survey_ref: str,
    survey_short_name: str,
    survey_id: str,
    unused_iac: str,
    permissions: dict,
) -> list:
    table = []
    for respondent in respondents:
        row = {}
        if permissions["reporting_unit_edit"]:
            if unused_iac:
                row["enrolment_code"] = unused_iac
            else:
                row["enrolment_code_hyperlink"] = url_for(
                    "reporting_unit_bp.generate_new_enrolment_code",
                    case_id=case_id,
                    collection_exercise_id=collection_exercise_id,
                    ru_name=ru_name,
                    ru_ref=sample_unit_ref,
                    trading_as=trading_as,
                    survey_ref=survey_ref,
                    survey_name=survey_short_name,
                )
                row["enrolment_code_hyperlink_text"] = "Generate new enrollment code"
        else:
            row["enrolment_code"] = ""
        row["contact_details"] = {
            "name": f"{respondent['firstName']} {respondent['lastName']}",
            "email": respondent["emailAddress"],
            "tel": respondent["telephone"],
        }
        row["account_status_class"] = (
            "ons-status--error" if respondent["status"] == "SUSPENDED" else "ons-status--success"
        )
        row["account_status"] = respondent["status"].capitalize()
        row["enrolment_status"] = respondent["enrolmentStatus"].capitalize()
        (
            row["enrolment_status_hyperlink"],
            row["enrolment_status_hyperlink_text"],
            row["enrolment_status_class"],
        ) = _build_enrollment_status_hyperlink(
            respondent["enrolmentStatus"],
            respondent["id"],
            respondent["firstName"],
            respondent["lastName"],
            sample_unit_ref,
            ru_name,
            ru_id,
            trading_as,
            survey_id,
            survey_short_name,
            permissions["reporting_unit_edit"],
        )
        if permissions["messages_edit"]:
            row["message"] = [
                {"name": "ru_ref", "value": sample_unit_ref},
                {"name": "business_id", "value": ru_id},
                {"name": "business", "value": ru_name},
                {"name": "survey", "value": survey_short_name},
                {"name": "survey_id", "value": survey_id},
                {"name": "msg_to_name", "value": row["contact_details"]["name"]},
                {"name": "msg_to", "value": respondent["id"]},
            ]
        table.append(row)

    return table


def _build_enrollment_status_hyperlink(
    enrolment_status: str,
    respondent_id: str,
    respondent_first_name: str,
    respondent_last_name: str,
    sample_unit_ref: str,
    ru_name: str,
    ru_id: str,
    trading_as: str,
    survey_id: str,
    survey_short_name: str,
    ru_permission: bool,
) -> tuple[str | None, str, str]:
    if enrolment_status == ENROLMENT_ENABLED:
        status_class = "ons-status--success"
        hyperlink = (
            url_for(
                "reporting_unit_bp.confirm_change_enrolment_status",
                ru_ref=sample_unit_ref,
                ru_name=ru_name,
                survey_id=survey_id,
                survey_name=survey_short_name,
                respondent_id=respondent_id,
                respondent_first_name=respondent_first_name,
                respondent_last_name=respondent_last_name,
                business_id=ru_id,
                trading_as=trading_as,
                change_flag="DISABLED",
                tab="reporting_units",
            )
            if ru_permission
            else None
        )
        hyperlink_text = "Disable"
    elif enrolment_status == ENROLMENT_PENDING:
        status_class = "ons-status--info"
        hyperlink = (
            url_for("reporting_unit_bp.view_resend_verification", ru_ref=sample_unit_ref, party_id=respondent_id)
            if ru_permission
            else None
        )
        hyperlink_text = "Re-send verification email"
    else:
        status_class = "ons-status--dead"
        hyperlink = (
            url_for(
                "reporting_unit_bp.confirm_change_enrolment_status",
                ru_ref=sample_unit_ref,
                ru_name=ru_name,
                survey_id=survey_id,
                survey_name=survey_short_name,
                respondent_id=respondent_id,
                respondent_first_name=respondent_first_name,
                respondent_last_name=respondent_last_name,
                business_id=ru_id,
                trading_as=trading_as,
                change_flag="ENABLED",
                tab="reporting_units",
            )
            if ru_permission
            else None
        )
        hyperlink_text = "Re-enable"

    return hyperlink, hyperlink_text, status_class
