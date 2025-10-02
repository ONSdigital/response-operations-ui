import pytest

from response_operations_ui import create_app


@pytest.fixture()
def app():
    return create_app("TestingConfig")


@pytest.fixture()
def survey():
    return {
        "id": "c23bb1c1-5202-43bb-8357-7a07c844308f",
        "shortName": "MWSS",
        "longName": "Monthly Wages and Salaries Survey",
        "surveyRef": "134",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "surveyMode": "EQ",
        "legalBasisRef": "STA1947",
        "eqVersion": "v2",
    }


@pytest.fixture()
def collection_exercise():
    return {
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
        "mapped_state": "Created",
        "exerciseRef": "021123",
        "userDescription": None,
        "created": "2023-11-02T16:52:03.029Z",
        "updated": None,
        "deleted": None,
        "validationErrors": None,
        "events": [],
        "sampleSize": None,
        "sampleLinks": [],
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
            "valid_cir_count": True,
            "ci_details": [
                {
                    "type": "eq",
                    "title": "EQ formtypes",
                    "url": "/surveys/MWSS/021123/view-sample-ci",
                    "link_text": "Choose",
                    "count": "0",
                }
            ],
        },
    }


@pytest.fixture()
def collection_instruments():
    return {
        "EQ": [
            {
                "classifiers": {"COLLECTION_EXERCISE": [], "RU_REF": [], "eq_id": "mbs", "form_type": "0001"},
                "file_name": "0001",
                "id": "ed5ad717-4367-499f-9f02-1e95f789c094",
                "surveyId": "0b1f8376-28e9-4884-bea5-acf9d709464e",
                "type": "EQ",
            }
        ]
    }


@pytest.fixture()
def event_value_dicts():
    return {
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


@pytest.fixture()
def event_in_the_past():
    return {
        "go_live": {
            "day": "Friday",
            "date": "03 Nov 2022",
            "month": "11",
            "time": "10:00",
            "is_in_future": False,
            "event_status": "SCHEDULED",
        }
    }


@pytest.fixture()
def dynamic_event():
    return {
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


@pytest.fixture()
def dynamic_event_deleted(dynamic_event):
    dynamic_event_deleted = dynamic_event.copy()
    del dynamic_event_deleted["reminder2"]
    return dynamic_event_deleted


@pytest.fixture()
def collection_exercises_with_details(collection_exercise):
    collection_exercises_with_details = collection_exercise.copy()
    collection_exercises_with_details["responseStatus"] = "Not started"
    collection_exercises_with_details["companyName"] = "RUNAME1_COMPANY1 RUNNAME2_COMPANY1 "
    collection_exercises_with_details["companyRegion"] = "GB"
    collection_exercises_with_details["tradingAs"] = "TOTAL UK ACTIVITY  "
    return [collection_exercises_with_details]


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
def multiple_collection_exercises_with_details(collection_exercises_with_details):
    multiple_collection_exercises_with_details = collection_exercises_with_details.copy()
    multiple_collection_exercises_with_details.append(collection_exercises_with_details[0].copy())
    multiple_collection_exercises_with_details[1]["responseStatus"] = "In progress"
    return multiple_collection_exercises_with_details


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
        "id": "a5348157-feb4-4bad-9614-fc76e2bfea94",
        "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
        "sampleSummaryId": "d646f19b-827f-4934-a71a-43ba458045b6",
        "sampleUnitRef": "49900000001",
        "sampleUnitType": "B",
        "trading_as": "TOTAL UK ACTIVITY",
    }


@pytest.fixture
def multiple_reporting_units(reporting_unit):
    multiple_reporting_units = reporting_unit.copy()
    multiple_reporting_units["associations"].append(
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
            "partyId": "985bf97e-4f03-4898-92ef-dd7aac23ab08",
        },
    )
    return multiple_reporting_units


@pytest.fixture()
def survey_respondents():
    return [
        {
            "enrolment_status": "ENABLED",
            "respondent": {
                "emailAddress": "example@example.com",
                "firstName": "john",
                "id": "bf19a18f-fe15-4005-b698-fdd36f35f940",
                "lastName": "doe",
                "sampleUnitType": "BI",
                "status": "ACTIVE",
                "telephone": "07772257772",
                "enrolmentStatus": "ENABLED",
            },
        }
    ]


@pytest.fixture
def multiple_survey_respondents(survey_respondents):
    multiple_survey_respondents = survey_respondents.copy()
    multiple_survey_respondents.append(survey_respondents[0].copy())
    return multiple_survey_respondents


@pytest.fixture
def suspended_survey_respondents(survey_respondents):
    suspended_survey_respondents = survey_respondents.copy()
    suspended_survey_respondents[0]["respondent"]["status"] = "SUSPENDED"
    return suspended_survey_respondents


@pytest.fixture
def pending_enrolment_survey_respondents(survey_respondents):
    pending_enrolment_survey_respondents = survey_respondents.copy()
    pending_enrolment_survey_respondents[0]["enrolment_status"] = "PENDING"
    return pending_enrolment_survey_respondents


@pytest.fixture
def disabled_enrolment_survey_respondents(survey_respondents):
    disabled_enrolment_survey_respondents = survey_respondents.copy()
    disabled_enrolment_survey_respondents[0]["enrolment_status"] = "DISABLED"
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


@pytest.fixture
def expected_ru_context():
    return {
        "collection_exercise_section": [
            {
                "hyperlink": "/case/49900000001/response-status?survey=MWSS&period=021123",
                "hyperlink_text": "Change",
                "period": "021123",
                "region": "GB",
                "reporting_unit_name": "RUNAME1_COMPANY1 " "RUNNAME2_COMPANY1 ",
                "response_status": "Not started",
                "status": {
                    "hyperlink": "/case/49900000001/response-status?survey=MWSS&period=021123",
                    "hyperlink_text": "Change",
                    "response_status": "Not started",
                    "status_class": "ons-status--info",
                },
                "status_class": "ons-status--info",
                "trading_as": "TOTAL UK ACTIVITY  ",
            }
        ],
        "respondents_section": [
            {
                "account_status": "Active",
                "account_status_class": "ons-status--success",
                "contact_details": {"email": "example@example.com", "name": "john doe", "tel": "07772257772"},
                "enrolment_status": "Enabled",
                "enrolment_status_class": "ons-status--success",
                "enrolment_status_hyperlink": "/reporting-units/49900000001/change-enrolment-status?"
                + "ru_name=RUNAME1_COMPANY1+RUNNAME2_COMPANY1&"
                + "survey_id=c23bb1c1-5202-43bb-8357-7a07c844308f&survey_name=134&"
                + "respondent_id=bf19a18f-fe15-4005-b698-fdd36f35f940&"
                + "respondent_first_name=john&respondent_last_name=doe&"
                + "business_id=a5348157-feb4-4bad-9614-fc76e2bfea94&"
                + "trading_as=TOTAL+UK+ACTIVITY++&"
                + "change_flag=DISABLED&tab=reporting_units",
                "enrolment_status_hyperlink_text": "Disable",
                "message": [
                    {"name": "ru_ref", "value": "49900000001"},
                    {"name": "business_id", "value": "a5348157-feb4-4bad-9614-fc76e2bfea94"},
                    {"name": "business", "value": "RUNAME1_COMPANY1 " "RUNNAME2_COMPANY1"},
                    {"name": "survey", "value": "MWSS"},
                    {"name": "survey_id", "value": "c23bb1c1-5202-43bb-8357-7a07c844308f"},
                    {"name": "msg_to_name", "value": "john doe"},
                    {"name": "msg_to", "value": "bf19a18f-fe15-4005-b698-fdd36f35f940"},
                ],
            }
        ],
    }


@pytest.fixture
def expected_ru_context_with_multiple_ces_and_respondents(expected_ru_context):
    expected_ru_context_with_multiple_ces_and_respondents = expected_ru_context.copy()
    expected_ru_context_with_multiple_ces_and_respondents["collection_exercise_section"].append(
        {
            "hyperlink": "/case/49900000001/response-status?survey=MWSS&period=021123",
            "hyperlink_text": "Change",
            "period": "021123",
            "region": "GB",
            "reporting_unit_name": "RUNAME1_COMPANY1 " "RUNNAME2_COMPANY1 ",
            "response_status": "In progress",
            "status": {
                "hyperlink": "/case/49900000001/response-status?survey=MWSS&period=021123",
                "hyperlink_text": "Change",
                "response_status": "In progress",
                "status_class": "ons-status--pending",
            },
            "status_class": "ons-status--pending",
            "trading_as": "TOTAL UK ACTIVITY  ",
        }
    )
    expected_ru_context_with_multiple_ces_and_respondents["respondents_section"].append(
        expected_ru_context["respondents_section"][0]
    )
    return expected_ru_context_with_multiple_ces_and_respondents


@pytest.fixture
def expected_response_status_context_for_complete_case():
    return {
        "change_response_status": {
            "radios_section": {
                "cancel_link": "/reporting-units/49900000001/surveys/02b9c366-7397-42f7-942a-76dc5876d86d",
                "confirm_button_variant": None,
                "radios": [{"id": "state-1", "label": {"text": "Not started"}, "value": "COMPLETED_TO_NOTSTARTED"}],
            },
            "url": "/case/49900000001/response-status?survey=QBS&"
            "case_group_id=6fef0397-f07b-4d65-8988-931cec23057f&period=1912",
        }
    }


@pytest.fixture
def expected_response_status_context_for_complete_case_status_change_disabled(
    expected_response_status_context_for_complete_case,
):
    expected_response_status_context_for_complete_case_after_48_hours = (
        expected_response_status_context_for_complete_case.copy()
    )
    expected_response_status_context_for_complete_case["change_response_status"]["radios_section"]["radios"][0][
        "attributes"
    ] = {"disabled": "true"}
    expected_response_status_context_for_complete_case["change_response_status"]["radios_section"]["radios"][0][
        "label"
    ]["description"] = "Status can only be changed after 48 hours have passed since the submission"
    expected_response_status_context_for_complete_case["change_response_status"]["radios_section"][
        "confirm_button_variant"
    ] = "disabled"
    return expected_response_status_context_for_complete_case_after_48_hours


@pytest.fixture
def expected_response_status_context_with_no_permissions():
    return {"change_response_status": {}}


@pytest.fixture
def expected_response_status_context_transitions_for_incomplete_case(
    expected_response_status_context_for_complete_case,
):
    expected_case_context_transitions_from_not_started = expected_response_status_context_for_complete_case.copy()
    expected_case_context_transitions_from_not_started["change_response_status"]["radios_section"]["radios"] = [
        {"id": "state-1", "label": {"text": "Completed by phone"}, "value": "COMPLETED_BY_PHONE"},
        {"id": "state-2", "label": {"text": "No longer required"}, "value": "NO_LONGER_REQUIRED"},
    ]
    return expected_case_context_transitions_from_not_started


@pytest.fixture
def transitions_for_complete_case():
    return {"COMPLETED_TO_NOTSTARTED": "Not started"}


@pytest.fixture
def transitions_for_incomplete_case():
    return {
        "COMPLETED_BY_PHONE": "Completed by phone",
        "NO_LONGER_REQUIRED": "No longer required",
    }


@pytest.fixture
def ru_ref():
    return "49900000001"


@pytest.fixture
def survey_short_name():
    return "QBS"


@pytest.fixture
def case_group_id():
    return "6fef0397-f07b-4d65-8988-931cec23057f"


@pytest.fixture
def ce_period():
    return "1912"


@pytest.fixture
def survey_id():
    return "02b9c366-7397-42f7-942a-76dc5876d86d"
