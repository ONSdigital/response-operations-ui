from datetime import datetime, timedelta

from response_operations_ui.contexts.case import build_response_status_context


def test_response_status_context_with_permissions(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case,
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
            datetime.now() - timedelta(seconds=300),
        )
    assert context == expected_response_status_context_for_complete_case


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
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

    assert (
        expected_response_status_context_transitions_for_incomplete_case["change_response_status"]["radios_section"]
        == radios_section
    )


def test_transitions_from_completed_by_phone(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case,
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
            datetime.now() - timedelta(seconds=300),
        )
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

        assert (
            expected_response_status_context_for_complete_case["change_response_status"]["radios_section"]
            == radios_section
        )


def test_transitions_from_no_longer_required(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case,
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
            datetime.now() - timedelta(seconds=300),
        )
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

        assert (
            expected_response_status_context_for_complete_case["change_response_status"]["radios_section"]
            == radios_section
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
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

        assert (
            expected_response_status_context_transitions_for_incomplete_case["change_response_status"]["radios_section"]
            == radios_section
        )


def test_transitions_from_complete(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case,
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
            datetime.now() - timedelta(seconds=300),
        )
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

        assert (
            expected_response_status_context_for_complete_case["change_response_status"]["radios_section"]
            == radios_section
        )


def test_transitions_from_complete_case_enabled(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case,
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
            datetime.now() - timedelta(seconds=300),
        )
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

        assert (
            expected_response_status_context_for_complete_case["change_response_status"]["radios_section"]
            == radios_section
        )


def test_transitions_from_complete_case_disabled(
    app,
    transitions_for_complete_case,
    expected_response_status_context_for_complete_case_status_change_disabled,
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
        radios_section = get_response_status_context_element(context, "change_response_status", "radios_section")

        assert (
            expected_response_status_context_for_complete_case_status_change_disabled["change_response_status"][
                "radios_section"
            ]
            == radios_section
        )


def get_response_status_context_element(context, section, element):
    return context[section][element]
