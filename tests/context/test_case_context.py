from datetime import datetime, timedelta

from response_operations_ui.contexts.case import build_response_status_context


def test_response_status_context_with_permissions(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_with_all_permissions,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            True,
            datetime.now(),
        )
    assert context == expected_response_status_context_for_complete_case_with_all_permissions


def test_response_status_context_without_permissions(
    app,
    transitions_for_complete_case,
    expected_response_status_context_with_no_permissions,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            False,
        )
    assert context == expected_response_status_context_with_no_permissions


def test_transitions_from_not_started(
    app,
    transitions_for_incomplete_case,
    expected_response_status_context_transitions_for_incomplete_case,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_incomplete_case,
            survey_id,
            True,
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_transitions_for_incomplete_case["change_response_status"]["radios"] == radios
    )


def test_transitions_from_completed_by_phone(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_with_all_permissions,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            True,
            datetime.now(),
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_for_complete_case_with_all_permissions["change_response_status"]["radios"]
        == radios
    )


def test_transitions_from_no_longer_required(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_with_all_permissions,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            True,
            datetime.now(),
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_for_complete_case_with_all_permissions["change_response_status"]["radios"]
        == radios
    )


def test_transitions_from_in_progress(
    app,
    transitions_for_incomplete_case,
    expected_response_status_context_transitions_for_incomplete_case,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_incomplete_case,
            survey_id,
            True,
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_transitions_for_incomplete_case["change_response_status"]["radios"] == radios
    )


def test_transitions_from_complete(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_with_all_permissions,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            True,
            datetime.now(),
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_for_complete_case_with_all_permissions["change_response_status"]["radios"]
        == radios
    )


def test_transitions_from_complete_after_48_hours(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_after_48_hours,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            True,
            datetime.now() - timedelta(days=3),
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_for_complete_case_after_48_hours["change_response_status"]["radios"] == radios
    )


def test_transitions_from_complete_within_48_hours(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_with_all_permissions,
    ru_ref,
    survey_short_name,
    case_group_id,
    ce_period,
    survey_id,
):
    with app.test_request_context():
        context = build_response_status_context(
            ru_ref,
            survey_short_name,
            case_group_id,
            ce_period,
            transitions_for_complete_case,
            survey_id,
            True,
            datetime.now(),
        )
        radios = get_response_status_context(context, "change_response_status", "radios")

    assert (
        expected_response_status_context_for_complete_case_with_all_permissions["change_response_status"]["radios"]
        == radios
    )


def get_response_status_context(context, section, element):
    return context[section][element]
