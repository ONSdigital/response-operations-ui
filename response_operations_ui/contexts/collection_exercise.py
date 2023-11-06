from flask import url_for

REMINDER_EMAILS = {
    "reminder": "First reminder",
    "reminder2": "Second reminder",
    "reminder3": "Third reminder",
    "reminder4": "Fourth reminder",
    "reminder5": "Fifth reminder",
}

NUDGE_EMAILS = {
    "nudge_email_0": "First nudge email",
    "nudge_email_1": "Second nudge email",
    "nudge_email_2": "Third nudge email",
    "nudge_email_3": "Fourth nudge email",
    "nudge_email_4": "Fifth nudge email",
}

CI_TABLE_LINK_TEXT = {
    "EQ": {"no_instrument": "Add", "restricted": "View", "has_permission": "Select or Add"},
    "SEFT": {"no_instrument": "Upload", "restricted": "View", "has_permission": "View or Upload"},
}


def build_ce_context(ce_details: dict, has_edit_permission: bool, locked: bool) -> dict:
    ce = ce_details["collection_exercise"]
    events = ce_details["events"]
    short_name = ce_details["survey"]["shortName"]
    survey_ref = ce_details["survey"]["surveyRef"]
    collection_instruments = ce_details["collection_instruments"]

    response_chasing = (
        _build_response_chasing(ce["id"], ce_details["survey"]["id"]) if ce["state"] in ("LIVE", "ENDED") else None
    )
    ci_table = _build_ci_table(
        collection_instruments,
        locked,
        ce_details["survey"]["surveyMode"],
        short_name,
        ce["exerciseRef"],
        has_edit_permission,
    )

    ce_info_events = _ce_events(ce, events)
    action_date_events = _action_date_events(events)
    ce_info = _build_event_section(ce, has_edit_permission, locked, ce_info_events, short_name, survey_ref)
    action_dates = _build_event_section(ce, has_edit_permission, locked, action_date_events, short_name, survey_ref)

    return {
        "ce_info": ce_info,
        "action_dates": action_dates,
        "response_chasing": response_chasing,
        "ci_table": ci_table,
    }


def _build_event_section(
    ce: dict, has_edit_permission: bool, locked: bool, section: dict, short_name: str, survey_ref: str
) -> dict:
    for event_type, event in section.items():
        event_value = event.get("value")
        in_the_future = True

        if isinstance(event_value, dict):
            event["text"] = " ".join([f"{event_value.get(format)}" for format in event.get("format")])
            event["status"] = event_value.get("event_status")
            in_the_future = event_value.get("is_in_future") if event["in_the_future_check"] else True
        else:
            event["text"] = event_value

        if has_edit_permission and (not locked or (event["editable_locked"] and in_the_future)):
            event["hyperlink"] = _build_url_for_event(ce, event_type, survey_ref, ce["exerciseRef"], short_name, event)
            event["hyperlink_text"] = (
                f'Edit {event["hyperlink_text"]}' if event_value else f'Add {event["hyperlink_text"]}'
            )
            html_hyperlink_id = event_type.replace("_", "-")
            event["hyperlink_id"] = (
                f"edit-event-date-{html_hyperlink_id}" if event_value else f"add-event-date-{html_hyperlink_id}"
            )
    return section


def _ce_events(ce: dict, events: dict) -> dict:
    return {
        "period_id": {
            "label": "Period ID *",
            "value": ce.get("exerciseRef"),
            "hyperlink_text": "ID",
            "editable_locked": False,
            "in_the_future_check": False,
        },
        "reporting_period": {
            "label": "Reporting period *",
            "value": ce.get("userDescription"),
            "hyperlink_text": "reporting period",
            "editable_locked": False,
            "in_the_future_check": False,
        },
        "ref_period_start": {
            "label": "Reference period start date *",
            "value": events.get("ref_period_start"),
            "format": ["day", "date"],
            "hyperlink_text": "start date",
            "editable_locked": True,
            "in_the_future_check": False,
        },
        "ref_period_end": {
            "label": "Reference period end date *",
            "value": events.get("ref_period_end"),
            "format": ["day", "date"],
            "hyperlink_text": "end date",
            "editable_locked": True,
            "in_the_future_check": False,
        },
        "employment": {
            "label": "Employment date",
            "value": events.get("employment"),
            "format": ["day", "date"],
            "hyperlink_text": "employment date",
            "editable_locked": True,
            "in_the_future_check": False,
        },
    }


def _action_date_events(events: dict) -> dict:
    action_dates = {
        "mps": {
            "label": "Main print selection *",
            "value": events.get("mps"),
            "format": ["day", "date", "time"],
            "hyperlink_text": "print date",
            "editable_locked": True,
            "in_the_future_check": True,
        },
        "go_live": {
            "label": "Go live *",
            "value": events.get("go_live"),
            "format": ["day", "date", "time"],
            "hyperlink_text": "go live date",
            "editable_locked": True,
            "in_the_future_check": True,
        },
    }
    if events.get("go_live") and events.get("return_by"):
        action_dates = action_dates | _build_dynamic_events(events, NUDGE_EMAILS, "nudge email")

    action_dates["return_by"] = {
        "label": "Return by *",
        "value": events.get("return_by"),
        "format": ["day", "date", "time"],
        "hyperlink_text": "return date",
        "editable_locked": True,
        "in_the_future_check": True,
    }
    action_dates = action_dates | _build_dynamic_events(events, REMINDER_EMAILS, "reminder")
    action_dates["exercise_end"] = {
        "label": "Exercise end *",
        "value": events.get("exercise_end"),
        "format": ["day", "date", "time"],
        "hyperlink_text": "end date",
        "editable_locked": True,
        "in_the_future_check": True,
    }

    return action_dates


def _build_dynamic_events(events: dict, events_to_create: dict, link_text: str) -> dict:
    dynamic_events = {}
    # An empty event should be added if available, however they can be deleted, so can become non-sequential
    # We still want to show all the ones with values, but only ever have one empty event at the lowest index
    empty_event_added = False
    for index, key in enumerate(events_to_create):
        event = events.get(key)

        if event or not empty_event_added:
            dynamic_events[key] = {
                "value": events.get(key),
                "label": events_to_create[key],
                "format": ["day", "date", "time"],
                "hyperlink_text": link_text,
                "editable_locked": True,
                "in_the_future_check": True,
            }

            if not event:
                dynamic_events[key]["label"] = "" if not index == 0 else dynamic_events[key]["label"]
                empty_event_added = True
    return dynamic_events


def _build_url_for_event(ce: dict, event_type: str, survey_ref: str, ref: str, survey_name: str, event: dict) -> str:
    if event_type == "period_id":
        return url_for(
            "collection_exercise_bp.edit_collection_exercise_period_id",
            short_name=survey_name,
            period=ref,
            surveyRef=survey_ref,
        )
    if event_type == "reporting_period":
        return url_for(
            "collection_exercise_bp.edit_collection_exercise_period_description",
            short_name=survey_name,
            period=ref,
            surveyRef=survey_ref,
        )

    if not event["value"]:
        return url_for(
            "collection_exercise_bp.get_create_collection_event_form",
            period=ref,
            short_name=survey_name,
            ce_id=ce["id"],
            tag=event_type,
        )

    return url_for(
        "collection_exercise_bp.update_event_date",
        period=ref,
        short_name=survey_name,
        tag=event_type,
    )


def _build_ci_table(
    ci: dict, locked: bool, survey_mode: str, short_name: str, exercise_ref: str, has_edit_permission
) -> dict:
    required_survey_mode_types = ["SEFT", "EQ"] if survey_mode == "EQ_AND_SEFT" else [survey_mode]
    ci_table_state_text = "restricted" if locked or not has_edit_permission else "has_permission"
    ci_details = []
    total_ci_count = 0
    for survey_mode_type in required_survey_mode_types:
        ci_count = len(ci.get(survey_mode_type, []))
        ci_table_state_text = "no_instrument" if ci_count == 0 else ci_table_state_text
        if survey_mode_type == "EQ":
            view_sample_ci_url = url_for(
                "collection_exercise_bp.get_view_sample_ci", short_name=short_name, period=exercise_ref
            )
        else:
            view_sample_ci_url = url_for(
                "collection_exercise_bp.get_seft_collection_instrument", period=exercise_ref, short_name=short_name
            )
        ci_details.append(
            {
                "type": survey_mode_type.lower(),
                "title": f"{survey_mode_type} collection instruments",
                "url": view_sample_ci_url,
                "link_text": CI_TABLE_LINK_TEXT[survey_mode_type][ci_table_state_text],
                "count": str(ci_count),
            }
        )
        total_ci_count += ci_count
    return {"total_ci_count": str(total_ci_count), "ci_details": ci_details}


def _build_response_chasing(ce_id: str, survey_id: str) -> dict:
    return {
        "xslx_url": url_for(
            "collection_exercise_bp.response_chasing", document_type="xslx", ce_id=ce_id, survey_id=survey_id
        ),
        "csv_url": url_for(
            "collection_exercise_bp.response_chasing", document_type="csv", ce_id=ce_id, survey_id=survey_id
        ),
    }
