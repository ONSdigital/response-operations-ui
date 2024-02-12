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


@pytest.fixture()
def collection_exercises_with_details():
    return [
        {
            "id": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
            "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
            "name": None,
            "actualExecutionDateTime": None,
            "scheduledExecutionDateTime": "2024-02-07T07:00:00.000Z",
            "scheduledStartDateTime": "2024-02-07T07:00:00.000Z",
            "actualPublishDateTime": None,
            "periodStartDateTime": "2024-02-07T07:00:00.000Z",
            "periodEndDateTime": "2024-02-12T07:00:00.000Z",
            "scheduledReturnDateTime": "2024-02-12T07:00:00.000Z",
            "scheduledEndDateTime": "2024-02-12T07:00:00.000Z",
            "executedBy": None,
            "eqVersion": "v3",
            "state": "LIVE",
            "exerciseRef": "1912",
            "userDescription": "December",
            "created": "2024-02-08T11:39:21.818Z",
            "updated": "2024-02-08T11:40:01.701Z",
            "deleted": None,
            "validationErrors": None,
            "events": [
                {
                    "id": "3efd51d9-b099-4fd9-9fb9-6f664faeb22f",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "employment",
                    "timestamp": "2024-02-07T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "991efd0e-dce4-4f75-b3ca-284f47851e1b",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "ref_period_start",
                    "timestamp": "2024-02-07T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "ccfde0be-717e-45e6-ac7e-bef2f9351a86",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "mps",
                    "timestamp": "2024-02-07T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "d2f1529b-9f74-494d-99d2-fb153f220312",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "go_live",
                    "timestamp": "2024-02-07T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "f5433dcd-c9db-4d9b-a56a-1d8a4b842a3e",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "reminder",
                    "timestamp": "2024-02-12T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "176d476a-14b2-4bf3-b260-e770dd4c123f",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "return_by",
                    "timestamp": "2024-02-12T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "66fad46a-3992-4d3e-8325-def6d0333b2f",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "exercise_end",
                    "timestamp": "2024-02-12T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "8d4bca94-8eae-4a07-a5e2-fa005cbb1d34",
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "tag": "ref_period_end",
                    "timestamp": "2024-02-12T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
            ],
            "sampleSize": 8,
            "sampleLinks": [
                {
                    "sampleLinkPK": 2,
                    "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
                    "sampleSummaryId": "d646f19b-827f-4934-a71a-43ba458045b6",
                }
            ],
            "responseStatus": "Not started",
            "companyName": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
            "companyRegion": "GB",
            "tradingAs": "TOTAL UK ACTIVITY  ",
        }
    ]


@pytest.fixture
def in_progress_collection_exercise_with_details(collection_exercises_with_details):
    in_progress_collection_exercise = collection_exercises_with_details.copy()
    in_progress_collection_exercise[0]["responseStatus"] = "In progress"
    return in_progress_collection_exercise


@pytest.fixture
def completed_collection_exercise_with_details(collection_exercises_with_details):
    completed_progress_collection_exercise = collection_exercises_with_details.copy()
    completed_progress_collection_exercise[0]["responseStatus"] = "Completed"
    return completed_progress_collection_exercise


@pytest.fixture
def no_longer_required_collection_exercise_with_details(collection_exercises_with_details):
    no_longer_required_collection_exercise = collection_exercises_with_details.copy()
    no_longer_required_collection_exercise[0]["responseStatus"] = "No longer required"
    return no_longer_required_collection_exercise


@pytest.fixture
def error_collection_exercise_with_details(collection_exercises_with_details):
    error_collection_exercise_with_details = collection_exercises_with_details.copy()
    error_collection_exercise_with_details[0]["responseStatus"] = "Error"
    return error_collection_exercise_with_details


@pytest.fixture
def multiple_collection_exercises_with_details():
    return [
        {
            "id": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
            "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
            "name": None,
            "actualExecutionDateTime": None,
            "scheduledExecutionDateTime": "2024-02-11T07:00:00.000Z",
            "scheduledStartDateTime": "2024-02-11T07:00:00.000Z",
            "actualPublishDateTime": None,
            "periodStartDateTime": "2024-02-11T07:00:00.000Z",
            "periodEndDateTime": "2024-02-16T07:00:00.000Z",
            "scheduledReturnDateTime": "2024-02-16T07:00:00.000Z",
            "scheduledEndDateTime": "2024-02-16T07:00:00.000Z",
            "executedBy": None,
            "eqVersion": "v3",
            "state": "LIVE",
            "exerciseRef": "1912",
            "userDescription": "December",
            "created": "2024-02-12T10:55:27.726Z",
            "updated": "2024-02-12T10:56:11.848Z",
            "deleted": None,
            "validationErrors": None,
            "events": [
                {
                    "id": "7e319653-aeb4-4c0a-a61a-29e2032a7798",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "employment",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "23dbdfec-ab00-4f48-a1da-b4bc52a2535e",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "ref_period_start",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "5203feba-6abd-41ba-b9a0-05772b4fbe78",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "mps",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "a0f7d120-18bf-44fb-9a26-d072d394929a",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "go_live",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "ae0d0a11-346c-420f-a330-f6a78197e526",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "reminder",
                    "timestamp": "2024-02-16T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "58dfcc65-894e-4007-a463-808cbe946cb5",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "return_by",
                    "timestamp": "2024-02-16T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "ecafc330-01c1-4f88-bc57-2dcf719a57ac",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "exercise_end",
                    "timestamp": "2024-02-16T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "c993524c-f790-4e4c-8af9-c04a0ca3e6d1",
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "tag": "ref_period_end",
                    "timestamp": "2024-02-16T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
            ],
            "sampleSize": 8,
            "sampleLinks": [
                {
                    "sampleLinkPK": 2,
                    "collectionExerciseId": "57e06b27-a62b-4d8e-8d57-7b6b80067e4f",
                    "sampleSummaryId": "72a7ffa5-0adb-476a-89d2-3ba54a004426",
                }
            ],
            "responseStatus": "Not started",
            "companyName": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
            "companyRegion": "GB",
            "tradingAs": "TOTAL UK ACTIVITY  ",
        },
        {
            "id": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
            "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
            "name": None,
            "actualExecutionDateTime": None,
            "scheduledExecutionDateTime": "2024-01-01T07:00:00.000Z",
            "scheduledStartDateTime": "2024-01-01T07:00:00.000Z",
            "actualPublishDateTime": None,
            "periodStartDateTime": "2024-01-01T07:00:00.000Z",
            "periodEndDateTime": "2024-02-12T11:30:00.000Z",
            "scheduledReturnDateTime": "2024-02-12T11:15:00.000Z",
            "scheduledEndDateTime": "2024-02-12T11:30:00.000Z",
            "executedBy": None,
            "eqVersion": "v3",
            "state": "ENDED",
            "exerciseRef": "202201",
            "userDescription": "January 2022",
            "created": "2024-02-12T11:01:19.667Z",
            "updated": "2024-02-12T11:30:03.959Z",
            "deleted": None,
            "validationErrors": None,
            "events": [
                {
                    "id": "52eec8dc-dcda-453d-baaf-d525e3097a63",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "ref_period_start",
                    "timestamp": "2024-01-01T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "79e0e3ef-2498-4fa1-986c-f73b166772d4",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "ref_period_end",
                    "timestamp": "2024-01-01T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "fe5278c4-2091-4a08-be92-119d76125546",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "employment",
                    "timestamp": "2024-01-01T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "efa0175a-db00-49d5-925d-bc24a04b9647",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "mps",
                    "timestamp": "2024-01-01T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "7ea5e6af-b05f-465d-974c-7a6cd91586bf",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "go_live",
                    "timestamp": "2024-01-01T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "4f736404-7b53-41d4-9b50-80b05f87176b",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "return_by",
                    "timestamp": "2024-02-12T11:15:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "dc26b3e0-09ef-4b31-b3c8-87023a6138fe",
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "tag": "exercise_end",
                    "timestamp": "2024-02-12T11:30:00.000Z",
                    "eventStatus": "PROCESSED",
                },
            ],
            "sampleSize": 8,
            "sampleLinks": [
                {
                    "sampleLinkPK": 3,
                    "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
                    "sampleSummaryId": "0b35dff1-07a3-4cfc-9eaf-2f01f6602e11",
                }
            ],
            "responseStatus": "In progress",
            "companyName": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
            "companyRegion": "GB",
            "tradingAs": "TOTAL UK ACTIVITY  ",
        },
    ]


@pytest.fixture()
def reporting_unit():
    return {
        "associations": [
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                "partyId": "bf19a18f-fe15-4005-b698-fdd36f35f940",
            }
        ],
        "attributes": {
            "birthdate": "01/09/1993",
            "cellNo": 7,
            "checkletter": "F",
            "currency": "S",
            "entname1": "ENTNAME1_COMPANY1",
            "entname2": "ENTNAME2_COMPANY1",
            "entname3": "",
            "entref": "9900000576",
            "entrepmkr": "E",
            "formType": "0001",
            "froempment": 8478,
            "frosic2007": "45320",
            "frosic92": "50300",
            "frotover": 801325,
            "inclexcl": "D",
            "legalstatus": "1",
            "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
            "region": "FE",
            "runame1": "RUNAME1_COMPANY1",
            "runame2": "RUNNAME2_COMPANY1",
            "runame3": "",
            "rusic2007": "45320",
            "rusic92": "50300",
            "sampleUnitId": "d8579750-8817-4a58-8fa5-867f1447e1cc",
            "seltype": "C",
            "trading_as": "TOTAL UK ACTIVITY",
            "tradstyle1": "TOTAL UK ACTIVITY",
            "tradstyle2": "",
            "tradstyle3": "",
        },
        "id": "a5348157-feb4-4bad-9614-fc76e2bfea94",
        "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
        "sampleSummaryId": "d646f19b-827f-4934-a71a-43ba458045b6",
        "sampleUnitRef": "49900000001",
        "sampleUnitType": "B",
        "trading_as": "TOTAL UK ACTIVITY",
    }


@pytest.fixture
def multiple_reporting_units():
    return {
        "associations": [
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                "partyId": "258b95c5-1e48-4357-881c-ad4d544eab32",
            },
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                "partyId": "985bf97e-4f03-4898-92ef-dd7aac23ab08",
            },
        ],
        "attributes": {
            "birthdate": "01/09/1993",
            "cellNo": 7,
            "checkletter": "F",
            "currency": "S",
            "entname1": "ENTNAME1_COMPANY1",
            "entname2": "ENTNAME2_COMPANY1",
            "entname3": "",
            "entref": "9900000576",
            "entrepmkr": "E",
            "formType": "0001",
            "froempment": 8478,
            "frosic2007": "45320",
            "frosic92": "50300",
            "frotover": 801325,
            "inclexcl": "D",
            "legalstatus": "1",
            "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
            "region": "FE",
            "runame1": "RUNAME1_COMPANY1",
            "runame2": "RUNNAME2_COMPANY1",
            "runame3": "",
            "rusic2007": "45320",
            "rusic92": "50300",
            "sampleUnitId": "68d27d0e-92b3-474e-af5f-3f9f7ad299a0",
            "seltype": "C",
            "trading_as": "TOTAL UK ACTIVITY",
            "tradstyle1": "TOTAL UK ACTIVITY",
            "tradstyle2": "",
            "tradstyle3": "",
        },
        "id": "3d6597e3-2bee-43d7-84e0-6f4f993240eb",
        "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
        "sampleSummaryId": "0b35dff1-07a3-4cfc-9eaf-2f01f6602e11",
        "sampleUnitRef": "49900000001",
        "sampleUnitType": "B",
        "trading_as": "TOTAL UK ACTIVITY",
    }


@pytest.fixture()
def survey_details():
    return {
        "id": "02b9c366-7397-42f7-942a-76dc5876d86d",
        "shortName": "QBS",
        "longName": "Quarterly Business Survey",
        "surveyRef": "139",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "surveyMode": "EQ",
        "legalBasisRef": "STA1947",
        "display_name": "139 QBS",
    }


@pytest.fixture()
def survey_respondents():
    return [
        {
            "associations": [
                {
                    "businessRespondentStatus": "ACTIVE",
                    "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                    "partyId": "a5348157-feb4-4bad-9614-fc76e2bfea94",
                    "sampleUnitRef": "49900000001",
                }
            ],
            "emailAddress": "example@example.com",
            "firstName": "john",
            "id": "bf19a18f-fe15-4005-b698-fdd36f35f940",
            "lastName": "doe",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "07772257772",
            "enrolmentStatus": "ENABLED",
        }
    ]


@pytest.fixture
def multiple_survey_respondents():
    return [
        {
            "associations": [
                {
                    "businessRespondentStatus": "ACTIVE",
                    "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                    "partyId": "3d6597e3-2bee-43d7-84e0-6f4f993240eb",
                    "sampleUnitRef": "49900000001",
                }
            ],
            "emailAddress": "example@example.com",
            "firstName": "john",
            "id": "258b95c5-1e48-4357-881c-ad4d544eab32",
            "lastName": "doe",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "07772257772",
            "enrolmentStatus": "ENABLED",
        },
        {
            "associations": [
                {
                    "businessRespondentStatus": "ACTIVE",
                    "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                    "partyId": "3d6597e3-2bee-43d7-84e0-6f4f993240eb",
                    "sampleUnitRef": "49900000001",
                }
            ],
            "emailAddress": "test@example.com",
            "firstName": "test",
            "id": "985bf97e-4f03-4898-92ef-dd7aac23ab08",
            "lastName": "test",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "1234567890",
            "enrolmentStatus": "ENABLED",
        },
    ]


@pytest.fixture
def suspended_survey_respondents(survey_respondents):
    suspended_survey_respondents = survey_respondents.copy()
    suspended_survey_respondents[0]["status"] = "SUSPENDED"
    return suspended_survey_respondents


@pytest.fixture
def pending_enrolment_survey_respondents(survey_respondents):
    pending_enrolment_survey_respondents = survey_respondents.copy()
    pending_enrolment_survey_respondents[0]["enrolmentStatus"] = "PENDING"
    return pending_enrolment_survey_respondents


@pytest.fixture
def disabled_enrolment_survey_respondents(survey_respondents):
    disabled_enrolment_survey_respondents = survey_respondents.copy()
    disabled_enrolment_survey_respondents[0]["enrolmentStatus"] = "DISABLED"
    return disabled_enrolment_survey_respondents


@pytest.fixture()
def case():
    return {
        "state": "ACTIONABLE",
        "id": "f4056be6-2581-4308-b7cd-88118325e81d",
        "actionPlanId": None,
        "activeEnrolment": True,
        "collectionInstrumentId": "e726f50c-504c-4958-be96-9d77520746b9",
        "partyId": "a5348157-feb4-4bad-9614-fc76e2bfea94",
        "sampleUnitId": "d8579750-8817-4a58-8fa5-867f1447e1cc",
        "iac": "t7jk7l29hymx",
        "caseRef": "1000000000000003",
        "createdBy": "SYSTEM",
        "sampleUnitType": "B",
        "createdDateTime": "2024-02-08T11:39:58.199Z",
        "caseGroup": {
            "collectionExerciseId": "1012f36c-b352-431c-b0c9-e7f435cbdd0c",
            "id": "39c7e488-3f06-4ea9-82fb-3c619f362cb6",
            "partyId": "a5348157-feb4-4bad-9614-fc76e2bfea94",
            "sampleUnitRef": "49900000001",
            "sampleUnitType": "B",
            "caseGroupStatus": "NOTSTARTED",
            "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
        },
        "caseEvents": None,
    }


@pytest.fixture
def multiple_cases():
    return {
        "state": "ACTIONABLE",
        "id": "5c298979-97ea-4db6-8c9c-324a91315f07",
        "actionPlanId": None,
        "activeEnrolment": True,
        "collectionInstrumentId": "c47b0ce2-1b40-4969-add4-832fa45c4179",
        "partyId": "3d6597e3-2bee-43d7-84e0-6f4f993240eb",
        "sampleUnitId": "68d27d0e-92b3-474e-af5f-3f9f7ad299a0",
        "iac": "99yk5r3yjycn",
        "caseRef": "1000000000000010",
        "createdBy": "SYSTEM",
        "sampleUnitType": "B",
        "createdDateTime": "2024-02-12T11:03:43.550Z",
        "caseGroup": {
            "collectionExerciseId": "f44feba3-c6e8-4e5f-a7ce-065ddc081424",
            "id": "00deae55-c74b-4ca2-a991-8b780c4550d6",
            "partyId": "3d6597e3-2bee-43d7-84e0-6f4f993240eb",
            "sampleUnitRef": "49900000001",
            "sampleUnitType": "B",
            "caseGroupStatus": "INPROGRESS",
            "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
        },
        "caseEvents": None,
    }


@pytest.fixture()
def unused_iac():
    return "p79j76f4pwfg"


@pytest.fixture()
def expected_ru_context_without_ru_permission():
    return {
        "collection_exercise_section": [
            {
                "status_class": "ons-status--info",
                "hyperlink": "/case/49900000001/response-status?survey=QBS&period=1912",
                "hyperlink_text": "View",
                "period": "1912",
                "reporting_unit_name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
                "trading_as": "TOTAL UK ACTIVITY  ",
                "region": "GB",
                "response_status": "Not started",
                "status": '<span class="ons-status ons-status--info">Not started</span>&nbsp;   '
                + '<a href="/case/49900000001/response-status?survey=QBS&period=1912">View</a>',
            }
        ],
        "respondents_section": [
            {
                "enrolment_code": "",
                "contact_details": {"Name": "john doe", "Email": "example@example.com", "Tel": "07772257772"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/>',
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "a5348157-feb4-4bad-9614-fc76e2bfea94"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "bf19a18f-fe15-4005-b698-fdd36f35f940"},
                ],
            }
        ],
    }


@pytest.fixture
def expected_ru_context_without_messages_permission():
    return {
        "collection_exercise_section": [
            {
                "status_class": "ons-status--info",
                "hyperlink": "/case/49900000001/response-status?survey=QBS&period=1912",
                "hyperlink_text": "Change",
                "period": "1912",
                "reporting_unit_name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
                "trading_as": "TOTAL UK ACTIVITY  ",
                "region": "GB",
                "response_status": "Not started",
                "status": '<span class="ons-status ons-status--info">Not started</span>&nbsp;  '
                + ' <a href="/case/49900000001/response-status?survey=QBS&period=1912">Change</a>',
            }
        ],
        "respondents_section": [
            {
                "enrolment_code_hyperlink": "/reporting-units/49900000001/new_enrolment_code?"
                + "case_id=f4056be6-2581-4308-b7cd-88118325e81d&"
                + "collection_exercise_id=1012f36c-b352-431c-b0c9-e7f435cbdd0c&"
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "trading_as=TOTAL+UK+ACTIVITY++&survey_ref=139&survey_name=QBS",
                "enrolment_code_hyperlink_text": "Generate new enrollment code",
                "contact_details": {"Name": "john doe", "Email": "example@example.com", "Tel": "07772257772"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/>'
                + ' <a href="/reporting-units/49900000001/change-enrolment-status?'
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "survey_id=02b9c366-7397-42f7-942a-76dc5876d86d&"
                + "survey_name=QBS&respondent_id=bf19a18f-fe15-4005-b698-fdd36f35f940&"
                + "respondent_first_name=john&respondent_last_name=doe&"
                + "business_id=a5348157-feb4-4bad-9614-fc76e2bfea94&"
                + "trading_as=TOTAL+UK+ACTIVITY&change_flag=DISABLED&"
                + 'tab=reporting_units"id="change-enrolment-status">Disable</a>',
            }
        ],
    }


@pytest.fixture
def expected_ru_context_with_all_permissions():
    return {
        "collection_exercise_section": [
            {
                "status_class": "ons-status--info",
                "hyperlink": "/case/49900000001/response-status?survey=QBS&period=1912",
                "hyperlink_text": "Change",
                "period": "1912",
                "reporting_unit_name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
                "trading_as": "TOTAL UK ACTIVITY  ",
                "region": "GB",
                "response_status": "Not started",
                "status": '<span class="ons-status ons-status--info">Not started</span>&nbsp;   '
                + '<a href="/case/49900000001/response-status?survey=QBS&period=1912">Change</a>',
            }
        ],
        "respondents_section": [
            {
                "enrolment_code_hyperlink": "/reporting-units/49900000001/new_enrolment_code?"
                + "case_id=f4056be6-2581-4308-b7cd-88118325e81d&"
                + "collection_exercise_id=1012f36c-b352-431c-b0c9-e7f435cbdd0c&"
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "trading_as=TOTAL+UK+ACTIVITY++&survey_ref=139&survey_name=QBS",
                "enrolment_code_hyperlink_text": "Generate new enrollment code",
                "contact_details": {"Name": "john doe", "Email": "example@example.com", "Tel": "07772257772"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/> '
                + '<a href="/reporting-units/49900000001/change-enrolment-status?'
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "survey_id=02b9c366-7397-42f7-942a-76dc5876d86d&"
                + "survey_name=QBS&respondent_id=bf19a18f-fe15-4005-b698-fdd36f35f940&"
                + "respondent_first_name=john&respondent_last_name=doe&"
                + "business_id=a5348157-feb4-4bad-9614-fc76e2bfea94&"
                + "trading_as=TOTAL+UK+ACTIVITY&change_flag=DISABLED&"
                + 'tab=reporting_units"id="change-enrolment-status">Disable</a>',
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "a5348157-feb4-4bad-9614-fc76e2bfea94"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "bf19a18f-fe15-4005-b698-fdd36f35f940"},
                ],
            }
        ],
    }


@pytest.fixture
def expected_ru_context_with_multiple_ces_and_respondents():
    return {
        "collection_exercise_section": [
            {
                "status_class": "ons-status--info",
                "hyperlink": "/case/49900000001/response-status?survey=QBS&period=1912",
                "hyperlink_text": "Change",
                "period": "1912",
                "reporting_unit_name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
                "trading_as": "TOTAL UK ACTIVITY  ",
                "region": "GB",
                "response_status": "Not started",
                "status": '<span class="ons-status ons-status--info">Not started</span>&nbsp;   '
                + '<a href="/case/49900000001/response-status?survey=QBS&period=1912">Change</a>',
            },
            {
                "status_class": "ons-status--pending",
                "hyperlink": "/case/49900000001/response-status?survey=QBS&period=202201",
                "hyperlink_text": "Change",
                "period": "202201",
                "reporting_unit_name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
                "trading_as": "TOTAL UK ACTIVITY  ",
                "region": "GB",
                "response_status": "In progress",
                "status": '<span class="ons-status ons-status--pending">In progress</span>&nbsp;   '
                + '<a href="/case/49900000001/response-status?survey=QBS&period=202201">Change</a>',
            },
        ],
        "respondents_section": [
            {
                "enrolment_code": "99yk5r3yjycn",
                "contact_details": {"Name": "john doe", "Email": "example@example.com", "Tel": "07772257772"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/> '
                + '<a href="/reporting-units/49900000001/change-enrolment-status?'
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "survey_id=02b9c366-7397-42f7-942a-76dc5876d86d&survey_name=QBS&"
                + "respondent_id=258b95c5-1e48-4357-881c-ad4d544eab32&respondent_first_name=john&"
                + "respondent_last_name=doe&business_id=3d6597e3-2bee-43d7-84e0-6f4f993240eb&"
                + "trading_as=TOTAL+UK+ACTIVITY&change_flag=DISABLED&"
                + 'tab=reporting_units"id="change-enrolment-status">Disable</a>',
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "3d6597e3-2bee-43d7-84e0-6f4f993240eb"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "258b95c5-1e48-4357-881c-ad4d544eab32"},
                ],
            },
            {
                "enrolment_code": "99yk5r3yjycn",
                "contact_details": {"Name": "test test", "Email": "test@example.com", "Tel": "1234567890"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/> '
                + '<a href="/reporting-units/49900000001/change-enrolment-status?'
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "survey_id=02b9c366-7397-42f7-942a-76dc5876d86d&survey_name=QBS&"
                + "respondent_id=985bf97e-4f03-4898-92ef-dd7aac23ab08&respondent_first_name=test&"
                + "respondent_last_name=test&business_id=3d6597e3-2bee-43d7-84e0-6f4f993240eb&"
                + "trading_as=TOTAL+UK+ACTIVITY&change_flag=DISABLED&"
                + 'tab=reporting_units"id="change-enrolment-status">Disable</a>',
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "3d6597e3-2bee-43d7-84e0-6f4f993240eb"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "test test"},
                    {"name": "msg_to", "value": "985bf97e-4f03-4898-92ef-dd7aac23ab08"},
                ],
            },
        ],
    }


@pytest.fixture
def expected_case_context_with_all_permissions():
    return {
        "change_response_status": {
            "form_action": "/case/49900000001/response-status?survey=QBS&"
            + "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
            "radios": [{"id": "state-1", "label": {"text": "Not started"}, "value": "COMPLETED_TO_NOTSTARTED"}],
            "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
        }
    }


@pytest.fixture
def expected_case_context_with_no_permissions():
    return {"change_response_status": {}}


@pytest.fixture
def expected_case_context_transitions_from_not_started():
    return {
        "change_response_status": {
            "form_action": "/case/49900000001/response-status?survey=QBS&"
            + "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
            "radios": [
                {"id": "state-1", "label": {"text": "Completed by phone"}, "value": "COMPLETED_BY_PHONE"},
                {"id": "state-2", "label": {"text": "No longer required"}, "value": "NO_LONGER_REQUIRED"},
            ],
            "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
        }
    }


@pytest.fixture
def expected_case_context_transitions_from_completed_by_phone():
    return {
        "change_response_status": {
            "form_action": "/case/49900000001/response-status?survey=QBS&"
            + "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
            "radios": [{"id": "state-1", "label": {"text": "Not started"}, "value": "COMPLETED_TO_NOTSTARTED"}],
            "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
        }
    }


@pytest.fixture
def expected_case_context_transitions_from_in_progress():
    return {
        "change_response_status": {
            "form_action": "/case/49900000001/response-status?survey=QBS&"
            + "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
            "radios": [
                {"id": "state-1", "label": {"text": "Completed by phone"}, "value": "COMPLETED_BY_PHONE"},
                {"id": "state-2", "label": {"text": "No longer required"}, "value": "NO_LONGER_REQUIRED"},
            ],
            "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
        }
    }


@pytest.fixture
def expected_case_context_transitions_from_no_longer_required():
    return {
        "change_response_status": {
            "form_action": "/case/49900000001/response-status?survey=QBS&"
            + "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
            "radios": [{"id": "state-1", "label": {"text": "Not started"}, "value": "COMPLETED_TO_NOTSTARTED"}],
            "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
        }
    }


@pytest.fixture
def expected_case_context_transitions_from_complete():
    return {
        "change_response_status": {
            "form_action": "/case/49900000001/response-status?survey=QBS&"
            + "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
            "radios": [{"id": "state-1", "label": {"text": "Not started"}, "value": "COMPLETED_TO_NOTSTARTED"}],
            "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
        }
    }


@pytest.fixture
def transitions_for_complete_case():
    return {"COMPLETED_TO_NOTSTARTED": "Not started"}


@pytest.fixture
def transitions_for_completed_by_phone_case():
    return {"COMPLETED_TO_NOTSTARTED": "Not started"}


@pytest.fixture
def transitions_for_no_longer_required_case():
    return {"COMPLETED_TO_NOTSTARTED": "Not started"}


@pytest.fixture
def transitions_for_in_progress_case():
    return {
        "COMPLETED_BY_PHONE": "Completed by phone",
        "NO_LONGER_REQUIRED": "No longer required",
    }


@pytest.fixture
def transitions_for_not_started_case():
    return {
        "COMPLETED_BY_PHONE": "Completed by phone",
        "NO_LONGER_REQUIRED": "No longer required",
    }
