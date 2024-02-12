from flask import url_for


def build_reporting_units_context(
    collection_exercises: list, ru: dict, survey: dict, respondents: list, case, unused_iac: str, permissions: list
):
    collection_exercise_section = _build_collection_exercise_section(collection_exercises, ru, survey, permissions)
    respondents_section = _build_respondents_section(
        respondents, case, collection_exercises, ru, survey, unused_iac, permissions
    )

    return {"collection_exercise_section": collection_exercise_section, "respondents_section": respondents_section}


def _build_collection_exercise_section(collection_exercises: list, ru: dict, survey: dict, permissions: list):
    table = []
    for ce in collection_exercises:
        row = {
            "status_class": _select_status_class(ce["responseStatus"]),
            "hyperlink": url_for(
                "case_bp.get_response_statuses",
                ru_ref=ru["sampleUnitRef"],
                survey=survey["shortName"],
                period=ce["exerciseRef"],
            ),
            "hyperlink_text": "Change" if permissions[0] else "View",
            "period": ce["exerciseRef"],
            "reporting_unit_name": ce["companyName"],
            "trading_as": ce["tradingAs"],
            "region": ce["companyRegion"],
            "response_status": ce["responseStatus"],
            "status": _build_ce_status(ru, survey, ce, permissions),
        }
        table.append(row)

    return table


def _select_status_class(status):
    if status == "Not started":
        return "ons-status--info"
    elif status == "In progress":
        return "ons-status--pending"
    elif status == "Completed" or status == "Completed by phone":
        return "ons-status--success"
    elif status == "No longer required":
        return "ons-status--dead"
    else:
        return "ons-status--error"


def _build_ce_status(ru, survey, ce, permissions):
    hyperlink = url_for(
        "case_bp.get_response_statuses",
        ru_ref=ru["sampleUnitRef"],
        survey=survey["shortName"],
        period=ce["exerciseRef"],
    )
    hyperlink_text = "Change" if permissions[0] else "View"
    status_class = _select_status_class(ce["responseStatus"])
    response_status = ce["responseStatus"]
    return (
        '<span class="ons-status '
        + status_class
        + '">'
        + response_status
        + "</span>"
        + "&nbsp;   "
        + '<a href="'
        + hyperlink
        + '">'
        + hyperlink_text
        + "</a>"
    )


def _build_respondents_section(
    respondents: list, case, collection_exercises: list, ru: dict, survey: dict, unused_iac: str, permissions: list
):
    table = []
    for respondent in respondents:
        row = {}
        if permissions[0]:
            if unused_iac:
                row["enrolment_code"] = unused_iac
            else:
                row["enrolment_code_hyperlink"] = url_for(
                    "reporting_unit_bp.generate_new_enrolment_code",
                    case_id=case["id"],
                    collection_exercise_id=collection_exercises[0]["id"],
                    ru_name=ru["name"],
                    ru_ref=ru["sampleUnitRef"],
                    trading_as=collection_exercises[0]["tradingAs"],
                    survey_ref=survey["surveyRef"],
                    survey_name=survey["shortName"],
                )
                row["enrolment_code_hyperlink_text"] = "Generate new enrollment code"
        else:
            row["enrolment_code"] = ""
        row["contact_details"] = {
            "Name": f"{respondent['firstName']} {respondent['lastName']}",
            "Email": respondent["emailAddress"],
            "Tel": respondent["telephone"],
        }
        row["account_status"] = (
            '<span class="ons-status '
            + _select_account_status_class(respondent["status"])
            + '">'
            + respondent["status"].capitalize()
            + "</span>"
        )
        row["enrolment_status"] = _build_enrolment_status(respondent, ru, survey, permissions)
        if permissions[1]:
            row["message"] = [
                {"name": "ru_ref", "value": ru["sampleUnitRef"]},
                {"name": "business_id", "value": ru["id"]},
                {"name": "business", "value": ru["name"]},
                {"name": "survey", "value": survey["shortName"]},
                {"name": "survey_id", "value": survey["id"]},
                {"name": "msg_to_name", "value": row["contact_details"]["Name"]},
                {"name": "msg_to", "value": respondent["id"]},
            ]
        table.append(row)

    return table


def _select_account_status_class(status):
    if status == "SUSPENDED":
        return "ons-status--error"
    else:
        return "ons-status--success"


def _build_enrollment_status_hyperlink(respondent, ru, survey, permissions):
    if respondent["enrolmentStatus"] == "ENABLED":
        status_class = "ons-status--success"
        hyperlink = url_for(
            "reporting_unit_bp.confirm_change_enrolment_status",
            ru_ref=ru["sampleUnitRef"],
            ru_name=ru["name"],
            survey_id=survey["id"],
            survey_name=survey["shortName"],
            respondent_id=respondent["id"],
            respondent_first_name=respondent["firstName"],
            respondent_last_name=respondent["lastName"],
            business_id=ru["id"],
            trading_as=ru["trading_as"],
            change_flag="DISABLED",
            tab="reporting_units",
        )
        hyperlink_text = "Disable"
    elif respondent["enrolmentStatus"] == "PENDING":
        status_class = "ons-status--info"
        hyperlink = url_for(
            "reporting_unit_bp.view_resend_verification", ru_ref=ru["sampleUnitRef"], party_id=respondent["id"]
        )
        hyperlink_text = "Re-send verification email"
    else:
        status_class = "ons-status--dead"
        hyperlink = url_for(
            "reporting_unit_bp.confirm_change_enrolment_status",
            ru_ref=ru["sampleUnitRef"],
            ru_name=ru["name"],
            survey_id=survey["id"],
            survey_name=survey["shortName"],
            respondent_id=respondent["id"],
            respondent_first_name=respondent["firstName"],
            respondent_last_name=respondent["lastName"],
            business_id=ru["id"],
            trading_as=ru["trading_as"],
            change_flag="ENABLED",
            tab="reporting_units",
        )
        hyperlink_text = "Re-enable"
    if not permissions[0]:
        hyperlink = None

    return hyperlink, hyperlink_text, status_class


def _build_enrolment_status(respondent, ru, survey, permissions):
    (
        hyperlink,
        hyperlink_text,
        enrolment_status_class,
    ) = _build_enrollment_status_hyperlink(respondent, ru, survey, permissions)
    enrolment_status = (
        '<span class="ons-status '
        + enrolment_status_class
        + '">'
        + respondent["enrolmentStatus"].capitalize()
        + "</span> <br/>"
    )
    enrolment_status_link = (
        ' <a href="' + hyperlink + '"id="change-enrolment-status">' + hyperlink_text + "</a>" if hyperlink else ""
    )
    enrolment_status = enrolment_status + enrolment_status_link
    return enrolment_status
