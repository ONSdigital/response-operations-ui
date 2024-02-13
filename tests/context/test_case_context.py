from response_operations_ui.contexts.case import build_response_status_context


def test_case_context_with_permissions(
    app,
    transitions_for_complete_case,
    expected_case_context_with_all_permissions,
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
        )
    assert context == expected_case_context_with_all_permissions


def test_case_context_without_permissions(
    app,
    transitions_for_complete_case,
    expected_case_context_with_no_permissions,
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
    assert context == expected_case_context_with_no_permissions


def test_transitions_from_not_started(
    app,
    transitions_for_not_started_case,
    expected_case_context_transitions_from_not_started,
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
            transitions_for_not_started_case,
            survey_id,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_not_started["change_response_status"]["radios"] == radios


def test_transitions_from_completed_by_phone(
    app,
    transitions_for_completed_by_phone_case,
    expected_case_context_transitions_from_completed_by_phone,
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
            transitions_for_completed_by_phone_case,
            survey_id,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_completed_by_phone["change_response_status"]["radios"] == radios


def test_transitions_from_no_longer_required(
    app,
    transitions_for_no_longer_required_case,
    expected_case_context_transitions_from_no_longer_required,
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
            transitions_for_no_longer_required_case,
            survey_id,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_no_longer_required["change_response_status"]["radios"] == radios


def test_transitions_from_in_progress(
    app,
    transitions_for_in_progress_case,
    expected_case_context_transitions_from_in_progress,
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
            transitions_for_in_progress_case,
            survey_id,
            True,
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_in_progress["change_response_status"]["radios"] == radios


def test_transitions_from_complete(
    app,
    transitions_for_complete_case,
    expected_case_context_transitions_from_complete,
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
        )
        radios = get_case_context(context, "change_response_status", "radios")

    assert expected_case_context_transitions_from_complete["change_response_status"]["radios"] == radios


def get_case_context(context, section, element):
    return context[section][element]
