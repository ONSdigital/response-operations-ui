from response_operations_ui.contexts.case import build_case_context

RU_REF = "49900000001"
SURVEY_SHORT_NAME = "QBS"
CASE_GROUP_ID = "6fef0397-f07b-4d65-8988-931cec23057f"
CE_PERIOD = "1912"
SURVEY_ID = "02b9c366-7397-42f7-942a-76dc5876d86d"


def test_case_context_with_permissions(app, transitions_for_complete_case, expected_case_context_with_all_permissions):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_complete_case,
            SURVEY_ID,
            True,
        )
    assert context == expected_case_context_with_all_permissions


def test_case_context_without_permissions(
    app, transitions_for_complete_case, expected_case_context_with_no_permissions
):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_complete_case,
            SURVEY_ID,
            False,
        )
    assert context == expected_case_context_with_no_permissions


def test_transitions_from_not_started(
    app, transitions_for_not_started_case, expected_case_context_transitions_from_not_started
):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_not_started_case,
            SURVEY_ID,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")
    
    assert expected_case_context_transitions_from_not_started["change_response_status"]["radios"] == radios


def test_transitions_from_completed_by_phone(
    app, transitions_for_completed_by_phone_case, expected_case_context_transitions_from_completed_by_phone
):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_completed_by_phone_case,
            SURVEY_ID,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_completed_by_phone["change_response_status"]["radios"] == radios


def test_transitions_from_no_longer_required(
    app, transitions_for_no_longer_required_case, expected_case_context_transitions_from_no_longer_required
):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_no_longer_required_case,
            SURVEY_ID,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_no_longer_required["change_response_status"]["radios"] == radios


def test_transitions_from_in_progress(
    app, transitions_for_in_progress_case, expected_case_context_transitions_from_in_progress
):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_in_progress_case,
            SURVEY_ID,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_in_progress["change_response_status"]["radios"] == radios


def test_transitions_from_complete(app, transitions_for_complete_case, expected_case_context_transitions_from_complete):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            transitions_for_complete_case,
            SURVEY_ID,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_complete["change_response_status"]["radios"] == radios


def get_case_context(context, section, element):
    return context[section][element]
