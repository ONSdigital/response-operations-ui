from response_operations_ui.contexts.case import build_case_context

RU_REF = "49900000001"
SURVEY_SHORT_NAME = "QBS"
CASE_GROUP_ID = "6fef0397-f07b-4d65-8988-931cec23057f"
CE_PERIOD = "1912"
COMPLETED_TO_NOTSTARTED_TRANSITION_FOR_CASE = {"COMPLETED_TO_NOTSTARTED": "Not started"}
SURVEY_ID = "02b9c366-7397-42f7-942a-76dc5876d86d"


def test_case_context_with_permissions(app, expected_case_context_with_all_permissions):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            COMPLETED_TO_NOTSTARTED_TRANSITION_FOR_CASE,
            SURVEY_ID,
            True,
        )
    assert context == expected_case_context_with_all_permissions


def test_case_context_without_permissions(app, expected_case_context_with_no_permissions):
    with app.test_request_context():
        context = build_case_context(
            RU_REF,
            SURVEY_SHORT_NAME,
            CASE_GROUP_ID,
            CE_PERIOD,
            COMPLETED_TO_NOTSTARTED_TRANSITION_FOR_CASE,
            SURVEY_ID,
            False,
        )
    assert context == expected_case_context_with_no_permissions
