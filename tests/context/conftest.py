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
