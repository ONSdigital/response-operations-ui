import pytest

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
    unused_iac,
    expected_ru_context_without_ru_permission,
):
    with app.test_request_context():
        context = build_reporting_units_context(
            collection_exercises_with_details, reporting_unit, survey_details, survey_respondents, case, unused_iac
        )
        status = get_ru_context(context, "collection_exercise_section", 0, "status")

    assert context == expected_ru_context_without_ru_permission
    assert "Change" not in status


def test_has_reporting_units_edit_permission():
    pass


def test_no_messages_edit_permission():
    pass


def test_has_messages_edit_permission():
    pass


def test_collection_exercises_dict():
    pass


def test_respondents_dict():
    pass


def test_respondent_enabled():
    pass


def test_respondent_disabled():
    pass


def get_ru_context(context, section, index, cell):
    return context[section][index][cell]
