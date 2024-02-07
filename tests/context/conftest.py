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
            "id": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
            "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
            "name": None,
            "actualExecutionDateTime": None,
            "scheduledExecutionDateTime": "2024-02-06T07:00:00.000Z",
            "scheduledStartDateTime": "2024-02-06T07:00:00.000Z",
            "actualPublishDateTime": None,
            "periodStartDateTime": "2024-02-06T07:00:00.000Z",
            "periodEndDateTime": "2024-02-11T07:00:00.000Z",
            "scheduledReturnDateTime": "2024-02-11T07:00:00.000Z",
            "scheduledEndDateTime": "2024-02-11T07:00:00.000Z",
            "executedBy": None,
            "eqVersion": "v3",
            "state": "LIVE",
            "exerciseRef": "1912",
            "userDescription": "December",
            "created": "2024-02-07T08:56:19.651Z",
            "updated": "2024-02-07T08:56:51.540Z",
            "deleted": None,
            "validationErrors": None,
            "events": [
                {
                    "id": "6d479451-213f-40ff-a6d0-a19dd67ac34b",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "employment",
                    "timestamp": "2024-02-06T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "acd9fe03-9987-49bc-a57a-cd8329255012",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "ref_period_start",
                    "timestamp": "2024-02-06T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "6f653bd3-5842-4d29-b2a4-cca031677072",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "mps",
                    "timestamp": "2024-02-06T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "58c5b8fe-1ec8-4b63-b6bb-32896d0266b6",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "go_live",
                    "timestamp": "2024-02-06T07:00:00.000Z",
                    "eventStatus": "PROCESSED",
                },
                {
                    "id": "1db88c85-86df-4110-9098-64fc9d75a44b",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "reminder",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "369aaeef-391a-48e4-8034-5dfb800f0dc3",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "return_by",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "1cb34037-8f64-49bb-958c-65e60e19a5a7",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "exercise_end",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
                {
                    "id": "c9361d17-95bd-4384-b6d6-d759e6e40086",
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "tag": "ref_period_end",
                    "timestamp": "2024-02-11T07:00:00.000Z",
                    "eventStatus": "SCHEDULED",
                },
            ],
            "sampleSize": 8,
            "sampleLinks": [
                {
                    "sampleLinkPK": 2,
                    "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
                    "sampleSummaryId": "2ec1cc1c-0772-4fbc-b52b-49110ab644fe",
                }
            ],
            "responseStatus": "Not started",
            "companyName": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 ",
            "companyRegion": "GB",
            "tradingAs": "TOTAL UK ACTIVITY  ",
        }
    ]


@pytest.fixture()
def reporting_unit():
    return {
        "associations": [
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                "partyId": "ab915b2a-2917-42c0-be12-cf464c524437",
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
            "sampleUnitId": "8cea7ea5-150e-457c-87e8-bf2c4d6226d3",
            "seltype": "C",
            "trading_as": "TOTAL UK ACTIVITY",
            "tradstyle1": "TOTAL UK ACTIVITY",
            "tradstyle2": "",
            "tradstyle3": "",
        },
        "id": "ece365f5-04a4-48fe-9029-ae6568cbe10b",
        "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
        "sampleSummaryId": "2ec1cc1c-0772-4fbc-b52b-49110ab644fe",
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
                    "partyId": "ece365f5-04a4-48fe-9029-ae6568cbe10b",
                    "sampleUnitRef": "49900000001",
                }
            ],
            "emailAddress": "example@example.com",
            "firstName": "john",
            "id": "ab915b2a-2917-42c0-be12-cf464c524437",
            "lastName": "doe",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "07772257772",
            "enrolmentStatus": "ENABLED",
        }
    ]


@pytest.fixture()
def case():
    return {
        "state": "ACTIONABLE",
        "id": "950bb30a-6a63-4132-8efe-6e4aca2e25ed",
        "actionPlanId": None,
        "activeEnrolment": True,
        "collectionInstrumentId": "aa684da7-f57c-4233-9be4-916cb8c89c05",
        "partyId": "ece365f5-04a4-48fe-9029-ae6568cbe10b",
        "sampleUnitId": "8cea7ea5-150e-457c-87e8-bf2c4d6226d3",
        "iac": "kvwsy5x3mtjv",
        "caseRef": "1000000000000006",
        "createdBy": "SYSTEM",
        "sampleUnitType": "B",
        "createdDateTime": "2024-02-07T08:56:51.130Z",
        "caseGroup": {
            "collectionExerciseId": "8a795a4d-8a02-4169-b9f1-103e1afbc0f1",
            "id": "2556693d-de77-4d96-9549-e3f750ce38c1",
            "partyId": "ece365f5-04a4-48fe-9029-ae6568cbe10b",
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
                    {"name": "business_id", "value": "ece365f5-04a4-48fe-9029-ae6568cbe10b"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "ab915b2a-2917-42c0-be12-cf464c524437"},
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
                "status": '<span class="ons-status ons-status--info">Not started</span>&nbsp;   '
                + '<a href="/case/49900000001/response-status?survey=QBS&period=1912">Change</a>',
            }
        ],
        "respondents_section": [
            {
                "enrolment_code": "p79j76f4pwfg",
                "contact_details": {"Name": "john doe", "Email": "example@example.com", "Tel": "07772257772"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/> '
                + '<a href="/reporting-units/49900000001/change-enrolment-status?ru_name='
                + "RUNAME1_COMPANY1+RUNNAME2_COMPANY1&survey_id="
                + "02b9c366-7397-42f7-942a-76dc5876d86d&survey_name=QBS&respondent_id="
                + "ab915b2a-2917-42c0-be12-cf464c524437&respondent_first_name=john"
                + "&respondent_last_name=doe&business_id=ece365f5-04a4-48fe-9029-ae6568cbe10b"
                + '&trading_as=TOTAL+UK+ACTIVITY&change_flag=DISABLED&tab=reporting_units">'
                + "Disable</a>",
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "ece365f5-04a4-48fe-9029-ae6568cbe10b"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "ab915b2a-2917-42c0-be12-cf464c524437"},
                ],
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
                "status": '<span class="ons-status ons-status--info">Not started</span>&nbsp;  '
                + ' <a href="/case/49900000001/response-status?survey=QBS&period=1912">Change</a>',
            }
        ],
        "respondents_section": [
            {
                "enrolment_code": "p79j76f4pwfg",
                "contact_details": {"Name": "john doe", "Email": "example@example.com", "Tel": "07772257772"},
                "account_status": '<span class="ons-status ons-status--success">Active</span>',
                "enrolment_status": '<span class="ons-status ons-status--success">Enabled</span> <br/> '
                + '<a href="/reporting-units/49900000001/change-enrolment-status?ru_name='
                + "RUNAME1_COMPANY1+RUNNAME2_COMPANY1&survey_id="
                + "02b9c366-7397-42f7-942a-76dc5876d86d&survey_name=QBS&respondent_id="
                + "ab915b2a-2917-42c0-be12-cf464c524437&respondent_first_name=john"
                + "&respondent_last_name=doe&business_id=ece365f5-04a4-48fe-9029-ae6568cbe10b"
                + '&trading_as=TOTAL+UK+ACTIVITY&change_flag=DISABLED&tab=reporting_units">'
                + "Disable</a>",
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "ece365f5-04a4-48fe-9029-ae6568cbe10b"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "QBS"},
                    {"name": "survey_id", "value": "02b9c366-7397-42f7-942a-76dc5876d86d"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "ab915b2a-2917-42c0-be12-cf464c524437"},
                ],
            }
        ],
    }
