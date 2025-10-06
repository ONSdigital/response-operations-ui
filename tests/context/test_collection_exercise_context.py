import pytest

from response_operations_ui.contexts.collection_exercise import build_ce_context

SURVEY_ID = "c23bb1c1-5202-43bb-8357-7a07c844308f"
CE_ID = "7702d7fd-f998-499d-a972-e2906b19e6cf"
PERIOD_ID_URL = "/surveys/MWSS/021123"
EXERCISE_ID_URL = f"{PERIOD_ID_URL}/{CE_ID}"


def test_no_edit_permission(app, collection_exercise, survey, expected_ce_context_no_permission):
    # Given a user has no edit permission
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, {}, False, False)
    period_id = _get_event_context(context, "ce_info", "period_id")

    # Then the context is built as expected with no hyperlinks
    assert context == expected_ce_context_no_permission
    assert "hyperlink" not in period_id


def test_has_edit_permission(app, collection_exercise, survey):
    # Given a user has edit permission and the exercise is not locked
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, {}, True, False)

    ref_period_start = _get_event_context(context, "ce_info", "ref_period_start")
    period_id = _get_event_context(context, "ce_info", "period_id")

    # Then empty events have 'add' hyperlinks and text, non-empty events have 'edit'.
    assert ref_period_start["text"] is None
    assert ref_period_start["hyperlink_text"] == "Add start date"
    assert ref_period_start["hyperlink"] == f"{EXERCISE_ID_URL}/confirm-create-event/ref_period_start"
    assert ref_period_start["hyperlink_id"] == "add-event-date-ref-period-start"

    assert period_id["text"] == "021123"
    assert period_id["hyperlink_text"] == "Edit ID"
    assert period_id["hyperlink"] == f"{PERIOD_ID_URL}/edit-collection-exercise-period-id?surveyRef=134"
    assert period_id["hyperlink_id"] == "edit-event-date-period-id"


def test_exercise_locked(app, collection_exercise, survey):
    # Given a user has edit permission and the exercise is locked
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, {}, True, True)

    ref_period_start = _get_event_context(context, "ce_info", "ref_period_start")
    period_id = _get_event_context(context, "ce_info", "period_id")

    # Then events which can be edited when locked have hyperlinks, ones that can't, don't.
    assert "hyperlink" in ref_period_start
    assert "hyperlink" not in period_id


def test_event_value_dicts(app, collection_exercise, survey, event_value_dicts):
    # Given a user has edit permission and the event value is a dict
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, event_value_dicts, True, False)

    go_live = _get_event_context(context, "action_dates", "go_live")

    # Then events text is formatted correctly
    assert go_live["text"] == "Friday 03 Nov 2023 10:00"


def test_event_reminders(app, collection_exercise, survey, dynamic_event):
    # Given there are 3 reminder events
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, dynamic_event, True, False)

    reminder = _get_event_context(context, "action_dates", "reminder")
    reminder2 = _get_event_context(context, "action_dates", "reminder2")
    reminder3 = _get_event_context(context, "action_dates", "reminder3")
    reminder4 = _get_event_context(context, "action_dates", "reminder4")

    # Then 3 reminders are generated with the correct label, text, hyperlink and link text.
    # An extra empty 'add' reminder with no label is also created
    assert "reminder" in context["action_dates"]
    assert reminder["label"] == "First reminder"
    assert reminder["hyperlink_text"] == "Edit reminder"
    assert "reminder2" in context["action_dates"]
    assert reminder2["label"] == "Second reminder"
    assert reminder2["hyperlink"] == f"{PERIOD_ID_URL}/event/reminder2"
    assert "reminder3" in context["action_dates"]
    assert reminder3["label"] == "Third reminder"
    assert reminder3["hyperlink_id"] == "edit-event-date-reminder3"

    assert "reminder4" in context["action_dates"]
    assert reminder4["label"] == ""
    assert reminder4["hyperlink_text"] == "Add reminder"
    assert reminder4["hyperlink"] == f"{EXERCISE_ID_URL}/confirm-create-event/reminder4"
    assert reminder4["hyperlink_id"] == "add-event-date-reminder4"


def test_event_middle_reminder_deleted(app, collection_exercise, survey, dynamic_event_deleted):
    # Given are 3 reminder events where one has been deleted (reminder 2 deleted, leaving reminder 1 and 3)
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, dynamic_event_deleted, True, True)

    reminder = _get_event_context(context, "action_dates", "reminder")
    reminder2 = _get_event_context(context, "action_dates", "reminder2")
    reminder3 = _get_event_context(context, "action_dates", "reminder3")

    # Then 2 reminders are generated with a 3rd empty 'add' reminder with no label at the lowest index (2)
    assert "reminder" in context["action_dates"]
    assert reminder["label"] == "First reminder"
    assert "reminder3" in context["action_dates"]
    assert reminder3["label"] == "Third reminder"

    assert "reminder2" in context["action_dates"]
    assert reminder2["label"] == ""
    assert "reminder4" not in context["action_dates"]


def test_locked_event_in_the_past(app, collection_exercise, survey, event_in_the_past):
    # Given the exercise is locked and an event is in the past
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, event_in_the_past, True, True)

    # Then there is no hyperlink to add/edit
    assert "hyperlink" not in context["action_dates"]["go_live"]


def test_not_locked_event_in_the_past(app, collection_exercise, survey, event_in_the_past):
    # Given the exercise is not locked and an event is in the past
    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, {}, event_in_the_past, True, False)

    # Then there is a hyperlink to add/edit
    assert "hyperlink" in context["action_dates"]["go_live"]


@pytest.mark.parametrize("status", ["Live", "Ended"])
def test_response_chasing(app, collection_exercise, survey, status):
    # Given the exercise is Live/Ended
    collection_exercise_updated = collection_exercise.copy()
    collection_exercise_updated["mapped_state"] = status

    # When build_ce_context is called
    with app.test_request_context():
        context = build_ce_context(collection_exercise_updated, survey, {}, {}, True, True)

    # Then response_chasing is populated correctly
    assert context["response_chasing"]["xslx_url"] == f"/surveys/response_chasing/xslx/{CE_ID}/{SURVEY_ID}"
    assert context["response_chasing"]["csv_url"] == f"/surveys/response_chasing/csv/{CE_ID}/{SURVEY_ID}"


def test_cir_and_ci_count_match(app, collection_exercise, survey, collection_instruments, mocker):
    mocker.patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service",
        return_value={"registry_instrument_count": 1},
    )
    app.config["CIR_ENABLED"] = True
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, collection_instruments, {}, True, False)

    assert context["ci_table"]["valid_cir_count"] is True


def test_cir_and_ci_count_dont_match(app, collection_exercise, survey, collection_instruments, mocker):
    mocker.patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service",
        return_value={"registry_instrument_count": 0},
    )
    app.config["CIR_ENABLED"] = True
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, collection_instruments, {}, True, False)

    assert context["ci_table"]["valid_cir_count"] is False


def test_ci_count_zero(app, collection_exercise, survey, collection_instruments, mocker):
    mocker.patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service",
        return_value={"registry_instrument_count": 0},
    )
    app.config["CIR_ENABLED"] = True
    with app.test_request_context():
        context = build_ce_context(collection_exercise, survey, collection_instruments, {}, True, False)

    #
    assert context["ci_table"]["valid_cir_count"] is False


def _get_event_context(context, parent, event):
    return context[parent][event]
