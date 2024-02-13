from response_operations_ui.contexts.reporting_units import (
    build_reporting_units_context,
)

REPORTING_UNITS = "49900000001"
SURVEY_ID = "c23bb1c1-5202-43bb-8357-7a07c844308f"


def test_no_reporting_units_edit_permission(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    survey_respondents,
    case,
    expected_ru_context_without_ru_permission,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": False, "messages_edit": True},
        )
        hyperlink = get_ru_context(context, "collection_exercise_section", 0, "status")["hyperlink_text"]

    assert context == expected_ru_context_without_ru_permission
    assert "Change" not in hyperlink
    assert "View" in hyperlink


def test_has_both_edit_permission(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    survey_respondents,
    case,
    expected_ru_context_with_all_permissions,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        hyperlink = get_ru_context(context, "collection_exercise_section", 0, "status")["hyperlink_text"]
        message = get_ru_context(context, "respondents_section", 0, "message")

    assert context == expected_ru_context_with_all_permissions
    assert "Change" in hyperlink
    assert message[0]["value"] == "49900000001"


def test_no_messages_edit_permission(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    survey_respondents,
    case,
    expected_ru_context_without_messages_permission,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": False},
        )

    assert context == expected_ru_context_without_messages_permission


def test_collection_exercise_in_progress(
    app, in_progress_collection_exercise_with_details, reporting_unit, survey_details, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            in_progress_collection_exercise_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--pending" in collection_exercise_status


def test_collection_exercise_completed(
    app, completed_collection_exercise_with_details, reporting_unit, survey_details, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            completed_collection_exercise_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--success" in collection_exercise_status


def test_collection_exercise_no_longer_required(
    app, no_longer_required_collection_exercise_with_details, reporting_unit, survey_details, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            no_longer_required_collection_exercise_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--dead" in collection_exercise_status


def test_collection_exercise_error(
    app, error_collection_exercise_with_details, reporting_unit, survey_details, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            error_collection_exercise_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--error" in collection_exercise_status


def test_respondent_active(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    survey_respondents,
    case,
    expected_ru_context_with_all_permissions,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        respondent_status = get_ru_context(context, "respondents_section", 0, "account_status_class")

    assert "ons-status--success" in respondent_status


def test_respondent_suspended(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    suspended_survey_respondents,
    case,
    expected_ru_context_with_all_permissions,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            suspended_survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        respondent_status = get_ru_context(context, "respondents_section", 0, "account_status_class")

    assert "ons-status--error" in respondent_status


def test_respondent_enrolment_enabled(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    survey_respondents,
    case,
    expected_ru_context_with_all_permissions,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        enrolment_status = get_ru_context(context, "respondents_section", 0, "enrolment_status_class")

    assert "ons-status--success" in enrolment_status


def test_respondent_enrolment_pending(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    pending_enrolment_survey_respondents,
    case,
    expected_ru_context_with_all_permissions,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            pending_enrolment_survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        enrolment_status = get_ru_context(context, "respondents_section", 0, "enrolment_status_class")

    assert "ons-status--info" in enrolment_status


def test_respondent_enrolment_disabled(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey_details,
    disabled_enrolment_survey_respondents,
    case,
    expected_ru_context_with_all_permissions,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey_details,
            disabled_enrolment_survey_respondents,
            case,
            "",
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        enrolment_status = get_ru_context(context, "respondents_section", 0, "enrolment_status_class")

    assert "ons-status--dead" in enrolment_status


def test_multiple_collection_exercises_and_respondents(
    app,
    multiple_collection_exercises_with_details,
    multiple_reporting_units,
    survey_details,
    multiple_survey_respondents,
    multiple_cases,
    expected_ru_context_with_multiple_ces_and_respondents,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            multiple_collection_exercises_with_details,
            multiple_reporting_units,
            survey_details,
            multiple_survey_respondents,
            multiple_cases,
            "99yk5r3yjycn",
            {"reporting_unit_edit": True, "messages_edit": True},
        )

    assert context == expected_ru_context_with_multiple_ces_and_respondents


def get_ru_context(context, section, index, cell):
    return context[section][index][cell]
