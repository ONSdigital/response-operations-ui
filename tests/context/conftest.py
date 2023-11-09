import pytest

from response_operations_ui import create_app


@pytest.fixture()
def app():
    return create_app("TestingConfig")


@pytest.fixture()
def ce_details():
    return {
        "survey": {
            "id": "c23bb1c1-5202-43bb-8357-7a07c844308f",
            "shortName": "MWSS",
            "longName": "Monthly Wages and Salaries Survey",
            "surveyRef": "134",
            "legalBasis": "Statistics of Trade Act 1947",
            "surveyType": "Business",
            "surveyMode": "EQ",
            "legalBasisRef": "STA1947",
            "eqVersion": "v2",
        },
        "collection_exercise": {
            "id": "7702d7fd-f998-499d-a972-e2906b19e6cf",
            "surveyId": "c23bb1c1-5202-43bb-8357-7a07c844308f",
            "name": None,
            "actualExecutionDateTime": None,
            "scheduledExecutionDateTime": None,
            "scheduledStartDateTime": None,
            "actualPublishDateTime": None,
            "periodStartDateTime": None,
            "periodEndDateTime": None,
            "scheduledReturnDateTime": None,
            "scheduledEndDateTime": None,
            "executedBy": None,
            "eqVersion": "v3",
            "state": "Created",
            "exerciseRef": "021123",
            "userDescription": None,
            "created": "2023-11-02T16:52:03.029Z",
            "updated": None,
            "deleted": None,
            "validationErrors": None,
            "events": [],
            "sampleSize": None,
            "sampleLinks": [],
        },
        "events": {},
        "sample_summary": None,
        "collection_instruments": {},
        "eq_ci_selectors": [],
    }


@pytest.fixture()
def expected_ce_context_no_permission():
    return {
        "ce_info": {
            "period_id": {
                "label": "Period ID *",
                "value": "021123",
                "hyperlink_text": "ID",
                "editable_locked": False,
                "in_the_future_check": False,
                "text": "021123",
            },
            "reporting_period": {
                "label": "Reporting period *",
                "value": None,
                "hyperlink_text": "reporting period",
                "editable_locked": False,
                "in_the_future_check": False,
                "text": None,
            },
            "ref_period_start": {
                "label": "Reference period start date *",
                "value": None,
                "format": ["day", "date"],
                "hyperlink_text": "start date",
                "editable_locked": True,
                "in_the_future_check": False,
                "text": None,
            },
            "ref_period_end": {
                "label": "Reference period end date *",
                "value": None,
                "format": ["day", "date"],
                "hyperlink_text": "end date",
                "editable_locked": True,
                "in_the_future_check": False,
                "text": None,
            },
            "employment": {
                "label": "Employment date",
                "value": None,
                "format": ["day", "date"],
                "hyperlink_text": "employment date",
                "editable_locked": True,
                "in_the_future_check": False,
                "text": None,
            },
        },
        "action_dates": {
            "mps": {
                "label": "Main print selection *",
                "value": None,
                "format": ["day", "date", "time"],
                "hyperlink_text": "print date",
                "editable_locked": True,
                "in_the_future_check": True,
                "text": None,
            },
            "go_live": {
                "label": "Go live *",
                "value": None,
                "format": ["day", "date", "time"],
                "hyperlink_text": "go live date",
                "editable_locked": True,
                "in_the_future_check": True,
                "text": None,
            },
            "return_by": {
                "label": "Return by *",
                "value": None,
                "format": ["day", "date", "time"],
                "hyperlink_text": "return date",
                "editable_locked": True,
                "in_the_future_check": True,
                "text": None,
            },
            "reminder": {
                "value": None,
                "label": "First reminder",
                "format": ["day", "date", "time"],
                "hyperlink_text": "reminder",
                "editable_locked": True,
                "in_the_future_check": True,
                "text": None,
            },
            "exercise_end": {
                "label": "Exercise end *",
                "value": None,
                "format": ["day", "date", "time"],
                "hyperlink_text": "end date",
                "editable_locked": True,
                "in_the_future_check": True,
                "text": None,
            },
        },
        "response_chasing": None,
        "ci_table": {
            "total_ci_count": "0",
            "ci_details": [
                {
                    "type": "eq",
                    "title": "EQ collection instruments",
                    "url": "/surveys/MWSS/021123/view-sample-ci",
                    "link_text": "Add",
                    "count": "0",
                }
            ],
        },
    }


@pytest.fixture()
def ce_details_event_value_dicts(ce_details):
    ce_details_event_value_dicts = ce_details.copy()
    ce_details_event_value_dicts["events"] = {
        "go_live": {
            "day": "Friday",
            "date": "03 Nov 2023",
            "month": "11",
            "time": "10:00",
            "is_in_future": True,
            "event_status": "SCHEDULED",
        },
        "return_by": {
            "day": "Friday",
            "date": "03 Nov 2024",
            "month": "11",
            "time": "10:00",
            "is_in_future": True,
            "event_status": "SCHEDULED",
        },
    }
    return ce_details_event_value_dicts


@pytest.fixture()
def ce_details_event_in_the_past(ce_details):
    ce_details_event_in_the_past = ce_details.copy()
    ce_details_event_in_the_past["events"] = {
        "go_live": {
            "day": "Friday",
            "date": "03 Nov 2022",
            "month": "11",
            "time": "10:00",
            "is_in_future": False,
            "event_status": "SCHEDULED",
        }
    }
    return ce_details_event_in_the_past


@pytest.fixture()
def ce_details_dynamic_event(ce_details):
    ce_details_dynamic_event = ce_details.copy()
    ce_details_dynamic_event["events"] = {
        "reminder": {
            "day": "Friday",
            "date": "04 Nov 2023",
            "month": "11",
            "time": "10:00",
            "is_in_future": True,
            "event_status": "SCHEDULED",
        },
        "reminder2": {
            "day": "Friday",
            "date": "05 Nov 2023",
            "month": "11",
            "time": "10:00",
            "is_in_future": True,
            "event_status": "SCHEDULED",
        },
        "reminder3": {
            "day": "Friday",
            "date": "05 Nov 2023",
            "month": "11",
            "time": "10:00",
            "is_in_future": True,
            "event_status": "SCHEDULED",
        },
    }
    return ce_details_dynamic_event


@pytest.fixture()
def ce_details_dynamic_event_deleted(ce_details_dynamic_event):
    ce_details_dynamic_event_deleted = ce_details_dynamic_event.copy()
    del ce_details_dynamic_event_deleted["events"]["reminder2"]
    return ce_details_dynamic_event_deleted
