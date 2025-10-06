from response_operations_ui.contexts.reporting_units import (
    build_reporting_units_context,
)


def test_has_both_edit_permission(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    survey_respondents,
    case,
    expected_ru_context,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        hyperlink = get_ru_context(context, "collection_exercise_section", 0, "status")["hyperlink_text"]
        message = get_ru_context(context, "respondents_section", 0, "message")

    assert context == expected_ru_context
    assert "Change" in hyperlink
    assert message[0]["value"] == "49900000001"


def test_no_reporting_units_edit_permission(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    survey_respondents,
    case,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": False, "messages_edit": True},
        )
        hyperlink = get_ru_context(context, "collection_exercise_section", 0, "status")["hyperlink_text"]

    assert "Change" not in hyperlink
    assert "View" in hyperlink


def test_no_messages_edit_permission(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    survey_respondents,
    case,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": False},
        )

    assert "message" not in context["respondents_section"][0].keys()


def test_collection_exercise_in_progress(
    app, in_progress_collection_exercise_with_details, reporting_unit, survey, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            in_progress_collection_exercise_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--pending" in collection_exercise_status


def test_collection_exercise_completed(
    app, completed_collection_exercise_with_details, reporting_unit, survey, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            completed_collection_exercise_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--success" in collection_exercise_status


def test_collection_exercise_no_longer_required(
    app, no_longer_required_collection_exercise_with_details, reporting_unit, survey, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            no_longer_required_collection_exercise_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--dead" in collection_exercise_status


def test_collection_exercise_error(
    app, error_collection_exercise_with_details, reporting_unit, survey, survey_respondents, case
):
    with app.test_request_context():
        context = build_reporting_units_context(
            error_collection_exercise_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        collection_exercise_status = get_ru_context(context, "collection_exercise_section", 0, "status_class")

    assert "ons-status--error" in collection_exercise_status


def test_respondent_active(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    survey_respondents,
    case,
    expected_ru_context,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        respondent_status = get_ru_context(context, "respondents_section", 0, "account_status_class")

    assert "ons-status--success" in respondent_status


def test_respondent_suspended(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    suspended_survey_respondents,
    case,
    expected_ru_context,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            suspended_survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        respondent_status = get_ru_context(context, "respondents_section", 0, "account_status_class")

    assert "ons-status--error" in respondent_status


def test_respondent_enrolment_enabled(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    survey_respondents,
    case,
    expected_ru_context,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        enrolment_status = get_ru_context(context, "respondents_section", 0, "enrolment_status_class")

    assert "ons-status--success" in enrolment_status


def test_respondent_enrolment_pending(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    pending_enrolment_survey_respondents,
    case,
    expected_ru_context,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            pending_enrolment_survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        enrolment_status = get_ru_context(context, "respondents_section", 0, "enrolment_status_class")

    assert "ons-status--info" in enrolment_status


def test_respondent_enrolment_disabled(
    app,
    collection_exercises_with_details,
    reporting_unit,
    survey,
    disabled_enrolment_survey_respondents,
    case,
    expected_ru_context,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details,
            reporting_unit,
            survey,
            disabled_enrolment_survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )
        enrolment_status = get_ru_context(context, "respondents_section", 0, "enrolment_status_class")

    assert "ons-status--dead" in enrolment_status


def test_multiple_collection_exercises_and_respondents(
    app,
    multiple_collection_exercises_with_details,
    multiple_reporting_units,
    survey,
    multiple_survey_respondents,
    case,
    expected_ru_context_with_multiple_ces_and_respondents,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            multiple_collection_exercises_with_details,
            multiple_reporting_units,
            survey,
            multiple_survey_respondents,
            {"reporting_unit_edit": True, "messages_edit": True},
        )

    assert context == expected_ru_context_with_multiple_ces_and_respondents


def get_ru_context(context, section, index, cell):
    return context[section][index][cell]
