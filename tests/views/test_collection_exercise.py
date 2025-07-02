import json
import os
from io import BytesIO
from unittest.mock import patch
from urllib.parse import urlencode, urlparse

import fakeredis
import jwt
import mock
import requests_mock
from mock import Mock

from config import TestingConfig
from response_operations_ui.controllers import collection_instrument_controllers
from response_operations_ui.exceptions.error_codes import ErrorCode
from response_operations_ui.exceptions.exceptions import ExternalApiError
from response_operations_ui.views.collection_exercise import (
    CIR_ERROR_MESSAGES,
    build_collection_exercise_details,
    get_existing_sorted_nudge_events,
    validate_file_extension_is_correct,
    validate_ru_specific_collection_instrument,
)
from tests.views import ViewTestCase
from tests.views.test_admin import url_permission_url, url_sign_in_data

ci_selector_id = "efa868fb-fb80-44c7-9f33-d6800a17c4da"
collection_exercise_event_id = "b4a36392-a21f-485b-9dc4-d151a8fcd565"
collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
collection_instrument_id = "a32800c5-5dc1-459d-9932-0da6c21d2ed2"
collection_instrument_id_2 = "5c5ca56f-8d15-426d-969a-9799d68d7971"
collection_instrument_id_3 = "bc0b2cdf-754c-4ffd-bab2-e30bf177ec80"
collection_instrument_id_4 = "912f8a05-8f9c-4d90-bff5-825f45775822"
period = "000000"
sample_summary_id = "1a11543f-eb19-41f5-825f-e41aca15e724"
short_name = "MBS"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_ref = "141"
cir_guid = "427d40e6-f54a-4512-a8ba-e4dea54ea3dc"
form_type = "0001"

project_root = os.path.dirname(os.path.dirname(__file__))

collex_root = f"{project_root}/test_data/collection_exercise/collection_exercise_details"
no_sample = collex_root + "_no_sample.json"
failed_validation = collex_root + "_failedvalidation.json"
collex_details = collex_root + ".json"

"""Load all the necessary test data"""
with open(collex_details) as json_data:
    collection_exercise_details = json.load(json_data)

with open(no_sample) as json_data:
    collection_exercise_details_no_sample = json.load(json_data)

with open(f"{project_root}/test_data/survey/edited_survey_ce_details.json") as json_data:
    updated_survey_info = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/exercise_data.json") as json_data:
    exercise_data = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details.json") as fp:
    formatted_collection_exercise_details = json.load(fp)

with open(f"{project_root}/test_data/collection_exercise/formatted_new_collection_exercise_details.json") as fp:
    formatted_new_collection_exercise_details = json.load(fp)

with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details.json") as seft:
    seft_collection_exercise_details = json.load(seft)

with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as json_data:
    collection_exercise = json.load(json_data)

with open(f"{project_root}/test_data/survey/single_survey.json") as json_data:
    survey = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/events.json") as json_data:
    events = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/nudge_events.json") as json_data:
    nudge_events = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/events_2030.json") as json_data:
    events_2030 = json.load(json_data)

with open(
    f"{project_root}/test_data/collection_exercise/collection_exercise_details_eq_both_ref_date.json"
) as json_data:
    collection_exercise_eq_both_ref_date = json.load(json_data)

with open(
    f"{project_root}/test_data/collection_exercise/collection_exercise_details_eq_ref_start_date.json"
) as json_data:
    collection_exercise_eq_ref_start_date = json.load(json_data)

with open(
    f"{project_root}/test_data/collection_exercise/collection_exercise_details_eq_ref_end_date.json"
) as json_data:
    collection_exercise_eq_ref_end_date = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/collection_exercise_details_sample_init_state.json") as fp:
    ce_details_sample_init_state = json.load(fp)

with open(f"{project_root}/test_data/collection_exercise/collection_exercise_pre_population.json") as fp:
    ce_with_pre_population = json.load(fp)

with open(f"{project_root}/test_data/sample/all_sample_units_loaded.json") as fp:
    all_sample_units_loaded = json.load(fp)

with open(f"{project_root}/test_data/sample/not_all_sample_units_loaded.json") as fp:
    not_all_sample_units_loaded = json.load(fp)

with open(f"{project_root}/test_data/cir/cir_metadata.json") as fp:
    cir_metadata = json.load(fp)

user_permission_surveys_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "surveys.edit", "type": "DIRECT"}],
}

user_permission_messages_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "messages.edit", "type": "DIRECT"}],
}

"""Define URLS"""
collection_exercise_root = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_ce_by_id = f"{collection_exercise_root}/{collection_exercise_id}"
url_ce_remove_sample = f"{collection_exercise_root}/unlink/{collection_exercise_id}/sample/{sample_summary_id}"
url_ces_by_survey = f"{collection_exercise_root}/survey/{survey_id}"
url_collection_exercise_link = f"{collection_exercise_root}/link/{collection_exercise_id}"
url_get_collection_exercises_link = f"{collection_exercise_root}/link/{collection_exercise_id}"
url_link_sample = f"{collection_exercise_root}/link/{collection_exercise_id}"
url_collection_exercise_survey_id = f"{collection_exercise_root}/survey/{survey_id}"
url_update_ce_user_details = f"{collection_exercise_root}/{collection_exercise_id}/userDescription"
url_update_ce_period = f"{collection_exercise_root}/{collection_exercise_id}/exerciseRef"
url_get_collection_exercise_events = f"{collection_exercise_root}/{collection_exercise_id}/events"
url_create_collection_exercise = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_execute = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexerciseexecution/{collection_exercise_id}"
url_get_by_survey_with_ref_end_date = f"{collection_exercise_root}/survey/{short_name}/{period}/event/ref_period_end?"

collection_instrument_root = f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2"
url_collection_instrument = f"{collection_instrument_root}/upload/{collection_exercise_id}"
url_collection_instrument_unlink = (
    f"{collection_instrument_root}/unlink-exercise/{collection_instrument_id}/{collection_exercise_id}"
)
url_collection_instrument_multi_select = f"{collection_instrument_root}/update-eq-instruments/{collection_exercise_id}"

url_post_instrument_link = f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2/upload"
url_get_collection_instrument = f"{collection_instrument_root}/collectioninstrument"
url_delete_collection_instrument = f"{collection_instrument_root}/delete/{collection_instrument_id}"

url_survey_shortname = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}"
url_get_survey_by_short_name = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}"

url_sample_service_upload = f"{TestingConfig.SAMPLE_FILE_UPLOADER_URL}/samples/fileupload"

url_get_sample_summary = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}"
url_get_sample_summary_status = (
    f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/"
    f"{sample_summary_id}/check-and-transition-sample-summary-status"
)
url_delete_sample_summary = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}"
url_check_if_all_sample_units_present_for_sample_summary = (
    f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}/check-and-transition-sample-summary-status"
)

url_get_by_survey_with_ref_start_date = (
    f"{collection_exercise_root}/survey/{short_name}/{period}/event/ref_period_start?"
)

url_party_delete_attributes = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/attributes/sample-summary/{sample_summary_id}"
)

url_cir_get_metadata = f"http://test.domain/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}"

ci_search_string = urlencode(
    {"searchString": json.dumps({"SURVEY_ID": survey_id, "COLLECTION_EXERCISE": collection_exercise_id})}
)

ci_type_search_string_eq = urlencode({"searchString": json.dumps({"SURVEY_ID": survey_id, "TYPE": "EQ"})})
ci_type_search_string_seft = urlencode({"searchString": json.dumps({"SURVEY_ID": survey_id, "TYPE": "SEFT"})})


def sign_in_with_permission(self, mock_request, permission):
    mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
    mock_request.get(url_permission_url, json=permission, status_code=200)
    self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})


class File:
    """Used to imitate a file being uploaded"""

    pass


class TestCollectionExercise(ViewTestCase):
    def setup_data(self):
        self.headers = {"Authorization": "test_jwt", "Content-Type": "application/json"}
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.survey_data = {"id": survey_id}
        self.seft_survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221",
            "eqVersion": "",
            "surveyMode": "SEFT",
        }
        self.eq_survey = {
            "id": survey_id,
            "longName": "Monthly Business Survey",
            "shortName": "MBS",
            "surveyRef": "009",
            "eqVersion": "",
            "surveyMode": "EQ",
        }
        self.eq_and_seft_survey = {
            "id": survey_id,
            "longName": "Monthly Business Survey",
            "shortName": "MBS",
            "surveyRef": "009",
            "eqVersion": "",
            "surveyMode": "EQ_AND_SEFT",
        }
        self.eq_survey_dates = {
            "id": survey_id,
            "longName": "Monthly Survey of Building Materials Bricks",
            "shortName": "MBS",
            "surveyRef": "074",
            "eqVersion": "v2",
            "surveyMode": "EQ",
            "ref_period_start": "2017-05-15T00:00:00Z",
            "ref_period_end": "2017-05-15T00:00:00Z",
        }
        self.collection_exercises = [
            {
                "id": collection_exercise_id,
                "name": "201601",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
                "state": "PUBLISHED",
                "exerciseRef": "000000",
                "events": [
                    {
                        "collectionExerciseId": "14fb3e68-4dca-46db-bf49-04b84e07e77c",
                        "eventStatus": "PROCESSED",
                        "id": "b4a36392-a21f-485b-9dc4-d151a8fcd565",
                        "tag": "mps",
                        "timestamp": "2018-03-16T00:00:00.000Z",
                    }
                ],
            }
        ]
        self.collection_exercise_events = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "mps",
                "timestamp": "2018-03-16T00:00:00.000Z",
                "eventStatus": "PROCESSED",
            },
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "go_live",
                "timestamp": "2018-03-17T00:00:00.000Z",
                "eventStatus": "RETRY",
            },
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "reminder",
                "timestamp": "2018-03-18T00:00:00.000Z",
                "eventStatus": "FAILED",
            },
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "reminder2",
                "timestamp": "2018-03-19T00:00:00.000Z",
                "eventStatus": "SCHEDULED",
            },
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "reminder3",
                "timestamp": "2018-03-20T00:00:00.000Z",
                "eventStatus": "PROCESSING",
            },
        ]
        self.collection_exercises_link = [sample_summary_id]
        self.eq_collection_instrument = [
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                    "form_type": "0001",
                },
                "file_name": "file",
                "id": collection_instrument_id,
                "surveyId": survey_id,
                "type": "EQ",
            },
        ]
        self.eq_multiple_collection_instrument = [
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                    "form_type": "form",
                },
                "file_name": "file",
                "id": collection_instrument_id,
                "surveyId": survey_id,
                "type": "EQ",
            },
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                    "form_type": "form",
                },
                "file_name": "file",
                "id": collection_instrument_id_2,
                "surveyId": survey_id,
                "type": "EQ",
            },
        ]
        self.seft_collection_instruments = [
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                },
                "file_name": "file",
                "id": collection_instrument_id,
                "surveyId": survey_id,
                "type": "SEFT",
            },
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                },
                "file_name": "file",
                "id": collection_instrument_id_2,
                "surveyId": survey_id,
                "type": "SEFT",
            },
        ]
        self.collection_exercise_ref_start_date = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "ref_period_start",
                "timestamp": "2018-03-16T00:00:00.000Z",
                "eventStatus": "PROCESSED",
            }
        ]
        self.collection_exercise_ref_end_date = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "ref_period_end",
                "timestamp": "2018-03-16T00:00:00.000Z",
                "eventStatus": "PROCESSED",
            }
        ]
        self.collection_exercise_ref_both_date = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "mps",
                "timestamp": "2018-03-16T00:00:00.000Z",
                "eventStatus": "PROCESSED",
            },
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "ref_period_start",
                "timestamp": "2018-03-16T00:00:00.000Z",
                "eventStatus": "PROCESSED",
            },
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "ref_period_end",
                "timestamp": "2018-03-16T00:00:00.000Z",
                "eventStatus": "PROCESSED",
            },
        ]
        self.eq_ci_selectors = [
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                    "form_type": "0001",
                },
                "file_name": None,
                "id": collection_instrument_id,
                "surveyId": survey_id,
                "type": "EQ",
            }
        ]
        self.sample_summary = {
            "id": sample_summary_id,
            "effectiveStartDateTime": "",
            "effectiveEndDateTime": "",
            "surveyRef": "",
            "ingestDateTime": "2018-03-14T14:29:51.325Z",
            "state": "ACTIVE",
            "totalSampleUnits": 8,
            "expectedCollectionInstruments": 1,
        }
        self.multi_select_response = [{"added": True}, {"removed": True}, {"added": True, "removed": True}]
        self.single_survey_eq = {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            "longName": "Monthly Business Survey",
            "shortName": "MBS",
            "surveyRef": "009",
            "surveyMode": "EQ",
        }

        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

    @requests_mock.mock()
    def test_collection_exercise_view_eq_non_ref_date(self, mock_request):
        self.load_eq_survey(
            mock_request,
            self.eq_survey_dates,
            self.collection_exercises,
            collection_exercise_details["collection_exercise"],
            self.collection_exercise_events,
            sample_summary_id,
            self.sample_summary,
            self.eq_collection_instrument,
            self.eq_ci_selectors,
        )
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_eq_ref_start_date(self, mock_request):
        self.load_eq_survey(
            mock_request,
            self.eq_survey_dates,
            self.collection_exercises,
            collection_exercise_details["collection_exercise"],
            self.collection_exercise_ref_start_date,
            sample_summary_id,
            self.sample_summary,
            self.eq_collection_instrument,
            self.eq_ci_selectors,
        )

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_eq_ref_end_date(self, mock_request):
        self.load_eq_survey(
            mock_request,
            self.eq_and_seft_survey,
            self.collection_exercises,
            collection_exercise_details["collection_exercise"],
            self.collection_exercise_ref_end_date,
            sample_summary_id,
            self.sample_summary,
            self.eq_collection_instrument,
            self.eq_ci_selectors,
        )

        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Business Survey".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_eq_both_ref_dates(self, mock_request):
        self.load_eq_survey(
            mock_request,
            self.eq_survey_dates,
            self.collection_exercises,
            collection_exercise_eq_both_ref_date["collection_exercise"],
            self.collection_exercise_ref_both_date,
            sample_summary_id,
            self.sample_summary,
            self.eq_collection_instrument,
            self.eq_ci_selectors,
        )
        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Set as ready for live".encode(), response.data)
        self.assertNotIn("Pre-Populated data is available for this sample".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_with_pre_population(self, mock_request):
        self.load_eq_survey(
            mock_request,
            self.eq_survey_dates,
            self.collection_exercises,
            ce_with_pre_population["collection_exercise"],
            self.collection_exercise_ref_both_date,
            sample_summary_id,
            self.sample_summary,
            self.eq_collection_instrument,
            self.eq_ci_selectors,
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Pre-Populated data is available for this sample".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.sample_controllers.sample_summary_state_check_required")
    def test_collection_exercise_update_ce_details(self, mock_request, mock_details):
        self.load_eq_survey(
            mock_request,
            self.eq_survey_dates,
            self.collection_exercises,
            collection_exercise_eq_both_ref_date["collection_exercise"],
            self.collection_exercise_ref_both_date,
            sample_summary_id,
            self.sample_summary,
            self.eq_collection_instrument,
            self.eq_ci_selectors,
        )
        # Not all sample units are loaded and therefore the ce is still in a scheduled state
        mock_request.get(url_ce_by_id, json=ce_details_sample_init_state["collection_exercise"])
        mock_request.get(
            url_check_if_all_sample_units_present_for_sample_summary,
            json=not_all_sample_units_loaded["sample_load_status"],
        )
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Created".encode(), response.data)
        # All sample units loaded and the ce is now in a Ready for review state
        mock_request.get(
            url_check_if_all_sample_units_present_for_sample_summary, json=all_sample_units_loaded["sample_load_status"]
        )
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_details.return_value = True
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for review".encode(), response.data)

    def load_eq_survey(
        self,
        mock_request,
        survey_short_name,
        collection_exercises,
        collex_details,
        collex_events,
        sample_summary_id,
        sample_summary,
        eq_ci,
        eq_ci_selectors,
    ):
        mock_request.get(url_get_survey_by_short_name, json=survey_short_name)
        mock_request.get(url_ces_by_survey, json=collection_exercises)
        mock_request.get(url_ce_by_id, json=collex_details)
        mock_request.get(url_get_collection_exercise_events, json=collex_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=sample_summary)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=eq_ci, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=eq_ci_selectors, complete_qs=True
        )

    @requests_mock.mock()
    def test_collection_exercise_view_seft(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=self.seft_collection_instruments,
            complete_qs=True,
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("PUBLISHED".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_eq_instrument(self, mock_details):
        # Given I have an eQ collection exercise with a collection instrument linked
        eq_cis = {"EQ": self.eq_collection_instrument}
        ce_details = {
            "survey": self.eq_survey_dates,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": eq_cis,
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        mock_details.return_value = ce_details

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view eQ collection instruments but not SEFT
        self.assertEqual(response.status_code, 200)
        self.assertIn("EQ formtypes".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertNotIn("SEFT collection instruments".encode(), response.data)
        self.assertNotIn('id="view-choose-upload-ci-seft">View</a>'.encode(), response.data)
        self.assertNotIn("CIR version".encode(), response.data)  # to be removed when CIR is live

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_cir(self, mock_details):
        # Given I have an eQ collection exercise with a collection instrument linked and CIR_ENABLED
        self.app.config["CIR_ENABLED"] = True
        eq_cis = {"EQ": self.eq_collection_instrument}
        ce_details = {
            "survey": self.eq_survey_dates,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": eq_cis,
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        mock_details.return_value = ce_details

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view eQ collection instruments and get a cir
        self.assertEqual(response.status_code, 200)
        self.assertIn("EQ formtypes".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertIn("CIR version".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_instruments(self, mock_details):
        # Given I have a SEFT collection exercise with collection instruments uploaded
        seft_cis = {"SEFT": self.seft_collection_instruments}
        ce_details = {
            "survey": self.seft_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": seft_cis,
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        mock_details.return_value = ce_details

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view SEFT collection instruments but not EQ
        self.assertEqual(response.status_code, 200)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-seft">View</a>'.encode(), response.data)
        self.assertNotIn("EQ formtypes".encode(), response.data)
        self.assertNotIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertNotIn("CIR version".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_eq_and_seft_instruments(self, mock_details):
        # Given I have an eQ and SEFT collection exercise with collection instruments for both
        eq_and_seft_cis = {"SEFT": self.seft_collection_instruments, "EQ": self.eq_collection_instrument}
        ce_details = {
            "survey": self.seft_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": eq_and_seft_cis,
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        ce_details["survey"]["surveyMode"] = "EQ_AND_SEFT"
        mock_details.return_value = ce_details

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view eQ and SEFT collection instruments for both
        self.assertEqual(response.status_code, 200)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("EQ formtypes".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-seft">View</a>'.encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_event_statuses(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Retry".encode(), response.data)
        self.assertIn("Failed".encode(), response.data)
        self.assertIn("Processing".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_exercise_states(self, mock_details):
        seft_collection_exercise_details["collection_exercise"]["state"] = "READY_FOR_REVIEW"
        mock_details.return_value = seft_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Set as ready for live".encode(), response.data)

        # Set the exercise state to READY_FOR_LIVE
        seft_collection_exercise_details["collection_exercise"]["state"] = "READY_FOR_LIVE"
        mock_details.return_value = seft_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

        # Set the exercise state to EXECUTION STARTED
        seft_collection_exercise_details["collection_exercise"]["state"] = "EXECUTION_STARTED"
        mock_details.return_value = seft_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

        # Set the exercise state to VALIDATED
        seft_collection_exercise_details["collection_exercise"]["state"] = "VALIDATED"
        mock_details.return_value = seft_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

        # Set the exercise state to EXECUTED
        seft_collection_exercise_details["collection_exercise"]["state"] = "EXECUTED"
        mock_details.return_value = seft_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

        # Set the exercise state to ENDED
        seft_collection_exercise_details["collection_exercise"]["state"] = "ENDED"
        mock_details.return_value = seft_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ended".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_details_single_eq_collection_instrument(self, mock_request):
        # Given I have a collection exercise with a single eq collection instrument (EQ)
        self._mock_build_collection_exercise_details(mock_request)

        # When I call build_collection_exercise_details
        with self.app.app_context():
            exercise_dict = build_collection_exercise_details("MBS", "000000", include_ci=True)

        # Then the collection exercise has 1 key (EQ) and 1 value in the collection instrument
        expected_output = {"EQ": self.eq_collection_instrument}
        self.assertEqual(expected_output, exercise_dict["collection_instruments"])
        self.assertEqual(len(exercise_dict["collection_instruments"]["EQ"]), 1)

    @requests_mock.mock()
    def test_collection_exercise_details_multiple_seft_collection_instruments(self, mock_request):
        # Given I have multiple collection instruments of the same type (2 x SEFT)
        eq_and_seft = self.seft_collection_instruments.copy()
        self._mock_build_collection_exercise_details(mock_request, False)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=eq_and_seft, complete_qs=True)

        # When I call build_collection_exercise_details
        with self.app.app_context():
            exercise_dict = build_collection_exercise_details("MBS", "000000", include_ci=True)

        # Then the collection exercise has 1 key (SEFT) and 2 values in the collection instrument
        expected_output = {"SEFT": eq_and_seft}

        self.assertEqual(expected_output, exercise_dict["collection_instruments"])
        self.assertEqual(len(exercise_dict["collection_instruments"]["SEFT"]), 2)
        self.assertEqual(exercise_dict["collection_instruments"]["SEFT"][0]["id"], collection_instrument_id)
        self.assertEqual(exercise_dict["collection_instruments"]["SEFT"][1]["id"], collection_instrument_id_2)

    @requests_mock.mock()
    def test_collection_exercise_details_eq_and_seft_collection_instruments(self, mock_request):
        # Given I have multiple collection instruments of different types (2 x SEFT, 1 x EQ)
        eq_and_seft_collection_instruments = self.seft_collection_instruments.copy()
        eq_and_seft_collection_instruments.append(self.eq_collection_instrument[0])
        self._mock_build_collection_exercise_details(mock_request, False)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=eq_and_seft_collection_instruments,
            complete_qs=True,
        )

        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        # When I call build_collection_exercise_details
        with self.app.app_context():
            exercise_dict = build_collection_exercise_details("MBS", "000000", include_ci=True)

        # Then the collection exercise has 2 keys (EQ and SEFT)
        # with 2 values in SEFT and 1 in EQ in the collection instrument
        expected_output = {"SEFT": self.seft_collection_instruments, "EQ": self.eq_collection_instrument}

        self.assertEqual(expected_output, exercise_dict["collection_instruments"])
        self.assertEqual(len(exercise_dict["collection_instruments"]["SEFT"]), 2)
        self.assertEqual(len(exercise_dict["collection_instruments"]["EQ"]), 1)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_sample_check_count(self, mock_request, mock_details):
        sample_status_json = {"areAllSampleUnitsLoaded": False, "expectedTotal": 10, "currentTotal": 5}
        mock_request.get(url_get_sample_summary_status, json=sample_status_json)
        mock_details.return_value = ce_details_sample_init_state

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Business Survey".encode(), response.data)
        self.assertIn("MBS 009".encode(), response.data)
        self.assertIn("Action dates".encode(), response.data)
        self.assertIn("Loading (5 / 10 loaded) …".encode(), response.data)
        self.assertIn("Refresh to see progress".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_sample_check_failed(self, mock_request, mock_details):
        mock_request.get(url_get_sample_summary_status, status_code=500)
        mock_details.return_value = ce_details_sample_init_state

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Business Survey".encode(), response.data)
        self.assertIn("MBS 009".encode(), response.data)
        self.assertIn("Sample summary check failed.  Refresh page to try again".encode(), response.data)
        self.assertIn("Action dates".encode(), response.data)
        # Note that the (current \ total) get completely removed if the call fails
        self.assertIn("Loading …".encode(), response.data)
        self.assertIn("Refresh to see progress".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_survey_errors(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)

        # Empty list
        mock_request.get(url_ces_by_survey, json=[])
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 500)

        # 204 returned (no surveys found with that id)
        mock_request.get(url_ces_by_survey, status_code=204)
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 500)

        # No match
        mock_request.get(url_ces_by_survey, json=[{"exerciseRef": "111111"}])
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_service_fail(self, mock_request):
        # 500 response back from survey
        mock_request.get(url_get_survey_by_short_name, status_code=500)
        response = self.client.get(f"/surveys/{short_name}/{period}")
        self.assertEqual(len(mock_request.request_history), 1)
        self.assertEqual(response.status_code, 500)

        # 400 Response back from collection instrument
        mock_request.reset()
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", status_code=400)
        response = self.client.get(f"/surveys/{short_name}/{period}")

        self.assertEqual(len(mock_request.request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_seft_collection_instrument(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-seft-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_eq_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-eq-ci": ""}
        ce_details = {
            "survey": self.eq_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": []},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[0], status_code=200)
        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_multiple_eq_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {
            "checkbox-answer": [collection_instrument_id, collection_instrument_id_2],
            "ce_id": collection_exercise_id,
            "select-eq-ci": "",
        }
        ce_details = {
            "survey": self.eq_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": []},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[0], status_code=200)
        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_eq_seft_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-eq-ci": ""}
        ce_details = {
            "survey": self.eq_and_seft_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": []},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[0], status_code=200)
        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_eq_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"checkbox-answer": [], "ce_id": collection_exercise_id, "select-eq-ci": ""}
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[1], status_code=200)

        ce_details = {
            "survey": self.eq_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": self.eq_multiple_collection_instrument},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }

        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_eq_seft_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"checkbox-answer": [], "ce_id": collection_exercise_id, "select-eq-ci": ""}
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[1], status_code=200)

        ce_details = {
            "survey": self.eq_and_seft_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": self.eq_collection_instrument},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }

        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_and_remove_eq_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {
            "checkbox-answer": [collection_instrument_id_2],
            "ce_id": collection_exercise_id,
            "select-eq-ci": "",
        }
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[2], status_code=200)

        ce_details = {
            "survey": self.eq_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": self.eq_collection_instrument},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }

        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_and_remove_multiple_eq_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {
            "checkbox-answer": [collection_instrument_id_3, collection_instrument_id_4],
            "ce_id": collection_exercise_id,
            "select-eq-ci": "",
        }
        mock_request.post(url_collection_instrument_multi_select, json=self.multi_select_response[2], status_code=200)

        ce_details = {
            "survey": self.eq_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": self.eq_multiple_collection_instrument},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }

        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers."
        "get_collection_instruments_by_classifier"
    )
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_add_eq_collection_instrument(
        self, mock_request, mock_details, mock_collective_cis, mock_get_linked_cis_and_cir_version
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-eq-ci": ""}
        mock_request.post(
            url_collection_instrument_multi_select,
            status_code=500,
            content=b'{"errors":["Error: ' b"Failed to add collection " b'instrument(s)"]}\n',
        )
        eq_ci_to_add = {"id": collection_instrument_id, "form_type": "0001", "checked": "true", "ci_version": None}
        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_collective_cis.return_value = eq_ci_to_add

        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=self.eq_collection_instrument,
            complete_qs=True,
            status_code=200,
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}",
            json=self.eq_ci_selectors,
            complete_qs=True,
            status_code=200,
        )

        ce_details = {
            "survey": self.eq_survey,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": {"EQ": []},
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
            "eq_ci_selectors": self.eq_collection_instrument,
        }

        mock_details.return_value = ce_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to add and remove collection instrument(s)".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise._redirect_with_error")
    def test_cir_no_ci_selected(self, redirect_with_error):
        self.app.config["CIR_ENABLED"] = True
        post_data = {"ce_id": collection_exercise_id, "select-eq-ci": ""}

        self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=False)

        redirect_with_error.assert_called_once_with("Choose one or more EQ formtypes to continue.", "000000", "MBS")

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_view_seft_collection_instrument_after_upload(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-seft-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_seft_collection_instrument_upload_validation(self, mock_details):
        mock_details.return_value = formatted_collection_exercise_details

        # Bad file extension
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Wrong file type for collection instrument".encode(), response.data)

        # Bad form type format
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

        # Bad file name format
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

        # Formtype isn't an integer
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

        # No file supplied
        post_data = {"load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_view_collection_instrument(self, mock_details):
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_another_collection_instrument_when_already_uploaded_no_permission(self, mock_details):
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data, response.data)
        self.assertNotIn("Remove SEFT file".encode(), response.data, response.data)
        self.assertNotIn("Add another collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_sample(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}

        sample_data = {"id": sample_summary_id}

        collection_exercise_link = {"id": ""}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.post(url_sample_service_upload, json=sample_data)
        mock_request.put(url_collection_exercise_link, json=collection_exercise_link)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Sample summary".encode(), response.data)
        self.assertIn("8\n".encode(), response.data)
        self.assertIn("1\n".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_sample_link_failure(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}
        sample_data = {"id": sample_summary_id}
        collection_exercise_link = {"id": ""}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=200, json=sample_data)
        mock_request.put(url_collection_exercise_link, status_code=500, json=collection_exercise_link)

        response = self.client.post(f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 8)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_upload_sample(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        data = {"sampleFile": (BytesIO(b"data"), "test.csv")}

        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}/upload-sample-file", data=data)

        request_history = mock_request.request_history
        self.assertEqual(response.status_code, 500)
        self.assertEqual(len(request_history), 7)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_sample_when_bad_extension(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        data = {"sampleFile": (BytesIO(b"data"), "test.html")}
        with open(
            f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details_no_sample.json"
        ) as collection_exercise_no_sample:
            mock_details.return_value = json.load(collection_exercise_no_sample)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Sample summary".encode(), response.data)
        self.assertIn("Invalid file format".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_sample_when_no_file(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        data = {"load-sample": ""}
        with open(
            f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details_no_sample.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Sample summary".encode(), response.data)
        self.assertIn("No file uploaded".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_sample_csv_too_few_columns(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}

        with open(
            f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details_no_sample.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=400, text="Too few columns in CSV file")

        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Sample summary".encode(), response.data)
        self.assertIn("Too few columns in CSV file".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_post_ready_for_live(self, mock_request, mock_details):
        post_data = {"ready-for-live": ""}
        details = formatted_collection_exercise_details.copy()
        details["collection_exercise"]["state"] = "EXECUTION_STARTED"
        mock_request.post(url_execute, status_code=200)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_details.return_value = details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_post_ready_for_live_404(self, mock_request, mock_details):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=404)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Error: Failed to execute Collection Exercise".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_empty(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=404)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)  # Redirect calls mocked requests 2 additional times
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_post_ready_for_live_failed(self, mock_request, mock_details):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=500)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Error: Failed to execute Collection Exercise".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_service_fail(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_get_processing(self, mock_details):
        details = formatted_collection_exercise_details.copy()
        details["collection_exercise"]["state"] = "EXECUTION_STARTED"
        mock_details.return_value = details

        response = self.client.get(f"/surveys/{short_name}/{period}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_execution(self, mock_details):
        with open(
            f"{project_root}/test_data/collection_exercise/"
            f"formatted_collection_exercise_details_failedvalidation.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)

        response = self.client.get(f"/surveys/{short_name}/{period}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for review".encode(), response.data)
        self.assertIn("Error processing collection exercise".encode(), response.data)
        self.assertNotIn("Incorrect file type. Please choose a file type XLSX".encode(), response.data)

    @requests_mock.mock()
    def test_update_collection_exercise_userdescription_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        test_description = "16th June 2019"
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": test_description,
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        mock_request.put(url_update_ce_user_details)

        response = self.client.post(
            f"/surveys/{short_name}/201906/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f"/surveys/{short_name}/201906")

    @requests_mock.mock()
    def test_update_collection_exercise_details_fail(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        mock_request.put(url_update_ce_user_details, status_code=500)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id", data=changed_ce_details
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_collection_exercise_details_404(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        mock_request.put(url_update_ce_user_details, status_code=404)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id", data=changed_ce_details
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_collection_exercise_period_fail(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        mock_request.put(url_update_ce_user_details, status_code=200)
        mock_request.put(url_update_ce_period, status_code=500)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_collection_exercise_period_404(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        mock_request.put(url_update_ce_user_details, status_code=200)
        mock_request.put(url_update_ce_period, status_code=404)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_get_ce_details(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(collection_exercise_id.encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_delete_seft_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        post_data = {
            "ci_id": collection_instrument_id,
            "delete-ci": "",
        }

        mock_request.delete(url_delete_collection_instrument, status_code=200)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument removed".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_delete_seft_collection_instrument_failure(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        post_data = {
            "ci_id": collection_instrument_id,
            "delete-ci": "",
        }

        mock_request.delete(url_delete_collection_instrument, status_code=404)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_get_create_collection_exercise(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        response = self.client.get(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "user_description": "New collection exercise",
            "period": period,
        }
        mock_request.register_uri(
            "GET",
            url_ces_by_survey,
            [{"json": {}, "status_code": 200}, {"json": self.collection_exercises, "status_code": 200}],
        )
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.post(url_create_collection_exercise, status_code=200)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment".encode(), response.data)
        self.assertIn(period.encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_period_already_exists(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        taken_period = "12345"
        new_collection_exercise_details = {
            "user_description": "New collection exercise",
            "period": taken_period,
        }
        ces = self.collection_exercises
        ces[0]["exerciseRef"] = taken_period
        mock_request.get(url_ces_by_survey, json=ces)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_create_collection_exercise_invalid_period(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "user_description": "New collection exercise",
            "period": "invalid",
        }
        mock_request.get(url_survey_shortname, status_code=200, json=self.seft_survey)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", data=new_collection_exercise_details
        )

        self.assertIn("Error creating collection exercise".encode(), response.data)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_edit_ce_validation_period_exists(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        taken_period = "12345"
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": taken_period,
            "hidden_survey_id": survey_id,
        }

        # update survey
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.put(url_update_ce_user_details)

        # failed validation
        ces = self.collection_exercises
        ces.append(ces[0])
        ces[1]["id"] = survey_id  # new id
        ces[1]["exerciseRef"] = taken_period
        mock_request.get(url_ces_by_survey, json=ces)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_edit_ce_validation_letters_in_period_fails_validation(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "hello",
            "hidden_survey_id": survey_id,
        }
        # update survey
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.put(url_update_ce_user_details)

        # failed validation
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_loaded_sample_success(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=204)
        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample removed".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_loaded_sample_failed_on_party(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_party_delete_attributes, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove sample".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_loaded_sample_failed_on_unlink(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove sample".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_loaded_sample_failed_on_sample(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # If the sample deletion fails, then there shouldn't be an error message
        self.assertNotIn("Error: Failed to remove sample".encode(), response.data)

    def test_get_confirm_remove_sample(self):
        response = self.client.get("/surveys/test/000000/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Remove sample from test 000000".encode(), response.data)

    @requests_mock.mock()
    def test_get_create_ce_event_form_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.get(
            f"/surveys/MBS/201801/{collection_exercise_id}/confirm-create-event/mps", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("MBS".encode(), response.data)
        self.assertIn("Main print selection".encode(), response.data)

    @requests_mock.mock()
    @mock.patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    @mock.patch("response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
    def test_create_collection_exercise_event_success(self, mock_request, mock_ce_events, mock_get_ce_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        with open(
            f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details_no_events.json"
        ) as collection_exercise:
            mock_get_ce_details.return_value = json.load(collection_exercise)
            mock_ce_events.return_value = None
        create_ce_event_form = {"day": "01", "month": "01", "year": "2030", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/MBS/201901/{collection_exercise_id}/create-event/mps",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Event date added.".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_invalid_form(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        create_ce_event_form = {"day": "50", "month": "01", "year": "2018", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/MBS/201801/{collection_exercise_id}/create-event/mps",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_collection_exercise_date_in_past(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        create_ce_event_form = {"day": "01", "month": "01", "year": "2018", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/MBS/201801/{collection_exercise_id}/create-event/mps",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertIn("Selected date can not be in the past".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @mock.patch("response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
    def test_create_collection_events_not_set_sequentially(self, mock_request, mock_ce_event):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)
        mock_ce_event.return_value = "Collection exercise events must be set sequentially"

        create_ce_event_form = {"day": "01", "month": "01", "year": "2029", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/MBS/201801/{collection_exercise_id}/create-event/reminder2",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection exercise events must be set sequentially".encode(), response.data)

    @requests_mock.mock()
    def test_schedule_nudge_email_option_not_present(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Schedule nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_schedule_nudge_email_option_present(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_can_create_up_to_five_nudge_email(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=nudge_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add nudge email".encode(), response.data)

        @requests_mock.mock()
        @mock.patch(
            "response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event"
        )
        def test_create_collection_events_not_set_sequentially(self, mock_request, mock_ce_event):
            mock_request.get(url_survey_shortname, json=survey)
            mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
            mock_request.get(url_get_collection_exercise_events, json=nudge_events)
            mock_ce_event.return_value = "Collection exercise events must be set sequentially"

            create_ce_event_form = {"day": "15", "month": "10", "year": "2018", "hour": "01", "minute": "00"}

            res = self.client.post(
                f"/surveys/MBS/201801/{collection_exercise_id}/create-event/nudge_email_4",
                data=create_ce_event_form,
                follow_redirects=True,
            )

            self.assertEqual(res.status_code, 200)
            self.assertIn("Nudge email must be set sequentially".encode(), res.data)

    def test_get_existing_sorted_nudge_events_for_no_nudge(self):
        res = get_existing_sorted_nudge_events([])
        self.assertEqual(res, [])

    def test_get_existing_sorted_nudge_events_for_sequential_nudge(self):
        nudge = {
            "nudge_email_0": {
                "day": "Saturday",
                "date": "06 Jun 2020",
                "month": "06",
                "time": "11:00",
                "is_in_future": True,
            },
            "nudge_email_3": {
                "day": "Saturday",
                "date": "06 Jun 2020",
                "month": "06",
                "time": "08:00",
                "is_in_future": True,
            },
            "nudge_email_4": {
                "day": "Saturday",
                "date": "06 Jun 2019",
                "month": "06",
                "time": "08:00",
                "is_in_future": True,
            },
        }
        res = get_existing_sorted_nudge_events(nudge)
        self.assertEqual(res, ["nudge_email_4", "nudge_email_3", "nudge_email_0"])

    @staticmethod
    def create_test_file():
        file = File()
        file.filename = "12345678901.xlsx"
        file.stream = "stream"
        file.mimetype = "mimetype"
        return file

    def test_validate_file_extension(self):
        """Test validation returns None when file extension is valid and an error dict when invalid"""
        file = self.create_test_file()
        self.assertIsNone(validate_file_extension_is_correct(file))

        file.filename = "12345678901.badext"
        error = validate_file_extension_is_correct(file)
        self.assertEqual(error["section"], "ciFile")
        self.assertEqual(error["header"], "Error: Wrong file type for collection instrument")
        self.assertEqual(error["message"], "Please use XLSX file only")

    def test_validate_ru_specific_collection_instrument(self):
        """Test validation returns None when file is correct and error dict if ru ref is not 11 digits"""
        file = self.create_test_file()
        self.assertIsNone(validate_ru_specific_collection_instrument(file, "12345678901"))

        file.filename = "1234567890.xlsx"
        error = validate_ru_specific_collection_instrument(file, "1234567890")
        self.assertEqual(error["section"], "ciFile")
        self.assertEqual(error["header"], "Error: Invalid file name format for ru specific collection instrument")
        self.assertEqual(error["message"], "Please provide a file with a valid 11 digit ru ref in the file name")

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_replace_sample_is_present(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_new_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Replace sample file".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_load_seft_collection_instruments_is_not_present(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        seft_collection_exercise_details["collection_instruments"] = {}
        mock_details.return_value = seft_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Upload SEFT collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_seft_upload_and_view_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data)
        self.assertIn("Remove".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_eq_and_seft_upload_collection_instrument_supports_xls(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xls"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_and_seft_survey)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data)
        self.assertIn("Remove".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.upload_collection_instrument")
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_seft_failed_upload_collection_instrument_with_error_message(
        self, mock_request, mock_details, mock_upload_ci
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_upload_ci.return_value = (False, "Error message passed")
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)
        self.assertIn("Error message passed".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.upload_collection_instrument")
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_seft_failed_upload_collection_instrument_without_error_message(
        self, mock_request, mock_details, mock_upload_ci
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_upload_ci.return_value = (False, None)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)
        self.assertIn("Please try again".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_seft_collection_instrument_when_bad_extension(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Wrong file type for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_seft_collection_instrument_when_bad_form_type_format(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_seft_collection_instrument_bad_file_name_format(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_seft_collection_instrument_form_type_not_integer(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_seft_collection_instrument_when_no_file(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @requests_mock.mock()
    def test_survey_edit_permission_collection_exercise(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Add".encode(), response.data)
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Add reminder".encode(), response.data)
        self.assertIn("Add nudge email".encode(), response.data)
        self.assertIn("Replace sample file".encode(), response.data)
        self.assertIn("Choose".encode(), response.data)

    @requests_mock.mock()
    def test_survey_edit_permission_collection_exercise_no_sample(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Add".encode(), response.data)
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Add reminder".encode(), response.data)
        self.assertIn("Add nudge email".encode(), response.data)
        self.assertIn("Upload sample file".encode(), response.data)
        self.assertIn("Choose".encode(), response.data)

    @requests_mock.mock()
    def test_no_survey_edit_permission_collection_exercise(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertNotIn("Upload sample file".encode(), response.data)

    @requests_mock.mock()
    def test_seft_load_collection_instruments_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details_no_sample["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=self.seft_collection_instruments,
            complete_qs=True,
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments")

        self.assertEqual(200, response.status_code)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("Upload SEFT collection instrument".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_eq_view_sample_ci_page_survey_permission(self, mock_request, mock_get_linked_cis_and_cir_version):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_get_linked_cis_and_cir_version.return_value = [{"form_type": "0001", "ci_version": None}]
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ")

        self.assertEqual(200, response.status_code)
        self.assertIn("Select EQ collection instruments".encode(), response.data)
        self.assertIn("checkbox-answer".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_eq_view_sample_ci_page_survey_permission_with_cir(self, mock_request, mock_get_linked_cis_and_cir_version):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)
        self.app.config["CIR_ENABLED"] = True
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ")

        self.assertEqual(200, response.status_code)
        self.assertIn("EQ formtype".encode(), response.data)
        self.assertIn("CIR version".encode(), response.data)
        self.assertIn("Continue to choose versions".encode(), response.data)

    @mock.patch(
        "response_operations_ui.controllers.collection_instrument_controllers.update_collection_exercise_eq_instruments"
    )
    @mock.patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_cir_post_select_eq_ci(self, collection_exercise_details, update_collection_exercise_eq_instruments):
        self.app.config["CIR_ENABLED"] = True
        collection_exercise_details.return_value = {
            "survey": {"surveyMode": "EQ"},
            "collection_exercise": {"id": collection_exercise_id},
        }
        update_collection_exercise_eq_instruments.return_value = 200, {}

        post_data = {
            "checkbox-answer": [collection_instrument_id],
            "ce_id": collection_exercise_id,
            "select-eq-ci": "",
        }
        response = self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(response.headers["Location"], f"/surveys/{short_name}/{period}/view-sample-ci/summary")

    @requests_mock.mock()
    def test_seft_loaded_load_collection_instruments_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=self.seft_collection_instruments,
            complete_qs=True,
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments")

        self.assertEqual(200, response.status_code)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("Upload SEFT collection instrument".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_seft_loaded_load_collection_instrument_page_no_survey_permission(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=self.seft_collection_instruments,
            complete_qs=True,
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments")

        self.assertEqual(200, response.status_code)
        self.assertIn("SEFT collection instruments uploaded".encode(), response.data)
        self.assertNotIn("Remove SEFT file".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_linked_ci_eq_view_sample_ci_page_survey_permission(
        self, mock_request, mock_get_linked_cis_and_cir_version
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ")

        self.assertEqual(200, response.status_code)
        self.assertIn("Select EQ collection instruments".encode(), response.data)
        self.assertIn("btn-add-ci".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_linked_ci_eq_view_sample_ci_page_no_survey_permission(
        self, mock_request, mock_details, mock_get_linked_cis_and_cir_version
    ):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)
        mock_details.return_value = self.get_ce_details()
        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ")

        self.assertEqual(200, response.status_code)
        self.assertIn("1 EQ collection instrument selected".encode(), response.data)
        self.assertNotIn("form-unselect-eq-ci-1".encode(), response.data)

    @requests_mock.mock()
    def test_loaded_sample_upload_sample_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/upload-sample-file")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertIn("Total businesses".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_upload_sample_page_no_survey_permission(self, mock_request):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/upload-sample-file")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have the required permission to "
            "access this function under your current role profile".encode(),
            response.data,
        )

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_sample_no_survey_permission(self, mock_request, mock_details):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}

        sample_data = {"id": sample_summary_id}

        collection_exercise_link = {"id": ""}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.post(url_sample_service_upload, json=sample_data)
        mock_request.put(url_collection_exercise_link, json=collection_exercise_link)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have the required permission to "
            "access this function under your current role profile".encode(),
            response.data,
        )

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_loaded_sample_no_survey_permission(self, mock_request, mock_details):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=204)
        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have the required permission to "
            "access this function under your current role profile".encode(),
            response.data,
        )

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_loaded_ci_load_collection_instrument_no_page_survey_permission(self, mock_details):
        mock_details.return_value = formatted_collection_exercise_details
        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Upload".encode(), response.data)
        self.assertNotIn("Choose file".encode(), response.data)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_load_ci_load_collection_instrument_page_no_survey_permission(self, mock_request, mock_details):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have the required permission to "
            "access this function under your current role profile".encode(),
            response.data,
        )

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_ci_load_collection_instrument_page_no_survey_permission(self, mock_request, mock_details):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-eq-ci": "",
        }

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have the required permission to "
            "access this function under your current role profile".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_collection_exercise_no_survey_edit_permission(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.eq_collection_instrument, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Add".encode(), response.data)
        self.assertNotIn("Edit".encode(), response.data)
        self.assertNotIn("Add nudge email".encode(), response.data)
        self.assertNotIn("Add reminder".encode(), response.data)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    def _mock_build_collection_exercise_details(self, mock_request, mock_ci_request=True):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        if mock_ci_request:
            mock_request.get(
                f"{url_get_collection_instrument}?{ci_search_string}",
                json=self.eq_collection_instrument,
                complete_qs=True,
            )

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_add_collection_instrument_success(self, mock_request, mock_get_linked_cis_and_cir_version):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]

        post_data = {"formtype": "0001", "add-eq-ci": ""}

        mock_request.get(url_survey_shortname, json=self.single_survey_eq)
        mock_request.post(
            f"{url_post_instrument_link}?survey_id={survey_id}&classifiers=%7B%22form_type%22%3A%220001%22%2C%22eq_id"
            f"%22%3A%22mbs%22%7D",
            status_code=200,
        )
        mock_request.get(f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=[], complete_qs=True)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_collection_exercise_link, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=[], complete_qs=True)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ",
            data=post_data,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(collection_instrument_id.encode(), response.data)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_add_collection_instrument_duplicate(self, mock_request, mock_get_linked_cis_and_cir_version):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"formtype": "0001", "add-eq-ci": ""}

        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_request.get(url_survey_shortname, json=self.single_survey_eq)

        mock_request.post(
            f"{url_post_instrument_link}?survey_id={survey_id}&classifiers=%7B%22form_type%22%3A%220001%22%2C%22eq_id"
            f"%22%3A%22mbs%22%7D",
            status_code=400,
            content=b'{"errors":["Failed to link collection instrument to survey"]}',
        )
        mock_request.get(f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=[], complete_qs=True)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_collection_exercise_link, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=self.eq_collection_instrument,
            complete_qs=True,
        )
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("There is a problem with this page".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.survey_controllers.get_survey_by_shortname")
    @patch(
        "response_operations_ui.views.collection_exercise."
        "collection_exercise_controllers.get_collection_exercises_by_survey"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_cis_and_cir_version")
    def test_view_sample_ci_summary(self, get_cis_and_cir_version, get_ce_by_survey, get_survey_by_shortname):
        get_survey_by_shortname.return_value = {"id": survey_id}
        get_ce_by_survey.return_value = [
            {"id": "d64cbfd2-20b1-4e10-962e-bd57f4946db7", "surveyId": survey_id, "exerciseRef": period}
        ]
        get_cis_and_cir_version.return_value = [
            {"form_type": "0001", "ci_version": "12"},
            {"form_type": "0002", "ci_version": None},
        ]

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/0001".encode(),
            response.data,
        )
        self.assertIn("Choose a version".encode(), response.data)
        self.assertIn("Edit version".encode(), response.data)
        self.assertIn("Version 12".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.survey_controllers.get_survey_by_shortname")
    @patch(
        "response_operations_ui.views.collection_exercise."
        "collection_exercise_controllers.get_collection_exercises_by_survey"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_cis_and_cir_version")
    def test_view_sample_ci_summary_no_cis(
        self, get_cis_and_cir_version, get_collection_exercises_by_survey, get_survey_by_shortname
    ):
        get_survey_by_shortname.return_value = {"id": survey_id}
        get_collection_exercises_by_survey.return_value = [
            {"id": "d64cbfd2-20b1-4e10-962e-bd57f4946db7", "surveyId": survey_id, "exerciseRef": period}
        ]
        get_cis_and_cir_version.return_value = []
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Choose a version".encode(), response.data)
        self.assertNotIn("Edit version".encode(), response.data)

    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_registry_instrument")
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    @patch("response_operations_ui.controllers.cir_controller.get_cir_metadata")
    def test_view_ci_versions_metadata_returned(
        self, mock_cir_metadata, mock_get_shortname, mock_details, mock_registry
    ):
        form_type = "0001"
        mock_details.return_value = self.get_ce_details()
        mock_cir_metadata.return_value = cir_metadata
        mock_get_shortname.return_value = {"short_name": {"survey_ref": survey_id}}
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(form_type.encode(), response.data)
        self.assertIn("Back to CIR versions".encode(), response.data)
        self.assertIn("Choose CIR version for EQ formtype".encode(), response.data)
        self.assertIn("Version 1".encode(), response.data)
        self.assertIn("Published: 16/07/2024 at 14:26:44".encode(), response.data)
        self.assertIn("Save".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    def test_save_ci_versions(self, mock_redis, mock_details):
        post_data = {"formtype": "0001", "ci-versions": "Version 1"}
        mock_details.return_value = self.get_ce_details()
        mock_redis.return_value = {"short_name": {"survey_ref": survey_id}}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/0001", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"/surveys/{short_name}/{period}".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    @patch("response_operations_ui.controllers.collection_instrument_controllers.delete_registry_instruments")
    @patch("response_operations_ui.views.collection_exercise.survey_controllers.get_survey_by_shortname")
    @patch(
        "response_operations_ui.views.collection_exercise."
        "collection_exercise_controllers.get_collection_exercises_by_survey"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_cis_and_cir_version")
    def test_delete_ci_versions(
        self,
        mock_collection_instrument,
        mock_collection_exercise,
        mock_delete_registry_instruments,
        mock_survey_id,
        mock_details,
    ):
        mock_details.return_value = self.get_ce_details()
        mock_survey_id.return_value = {"id": survey_id}
        mock_collection_exercise.return_value = self.collection_exercises
        mock_delete_registry_instruments.return_value = {"status_code": 200}
        mock_collection_instrument.return_value = [{"form_type": "0001", "ci_version": None}]

        post_data = {"formtype": "0001", "ci-versions": "nothing-selected", "period": period}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/0001", data=post_data, follow_redirects=True
        )
        self.assertIn(f"/surveys/{short_name}/{period}/view-sample-ci/summary".encode(), response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instruments step 2 of 2".encode(), response.data)
        self.assertIn(form_type.encode(), response.data)
        self.assertIn("Nothing selected".encode(), response.data)

    @patch("requests.get")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_view_ci_versions_no_metadata(self, mock_details, mock_redis, mock_response):
        form_type = "0001"
        mock_details.return_value = self.get_ce_details()
        mock_response = mock_response.return_value
        mock_response.url.return_value = url_cir_get_metadata
        mock_response.status_code.return_value = "404"
        mock_response.message.return_value = "No results found"
        mock_redis.return_value = {"short_name": {"survey_ref": survey_id}}

        with patch(
            "response_operations_ui.controllers.cir_controller.get_cir_metadata",
            Mock(side_effect=ExternalApiError(mock_response, ErrorCode.NOT_FOUND)),
        ):
            response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Choose CIR version for EQ formtype".encode(), response.data)
            self.assertIn(CIR_ERROR_MESSAGES[ErrorCode.NOT_FOUND].encode(), response.data)

    @patch("requests.get")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_view_ci_versions_unable_to_connect_to_cir(self, mock_details, mock_redis, mock_response):
        collection_instrument_controllers.get_registry_instrument = Mock()
        form_type = "0001"
        mock_details.return_value = self.get_ce_details()
        mock_response = mock_response.return_value
        mock_response.url.return_value = url_cir_get_metadata
        mock_response.status_code.return_value = "E0001"
        mock_response.message.return_value = "Unable to connect to CIR"
        mock_redis.return_value = {"short_name": {"survey_ref": survey_id}}

        with patch(
            "response_operations_ui.controllers.cir_controller.get_cir_metadata",
            Mock(side_effect=ExternalApiError(mock_response, ErrorCode.API_CONNECTION_ERROR)),
        ):
            response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Choose CIR version for EQ formtype".encode(), response.data)
            self.assertIn(CIR_ERROR_MESSAGES[ErrorCode.API_CONNECTION_ERROR].encode(), response.data)

    def get_ce_details(self):
        eq_cis = {"EQ": self.eq_ci_selectors}
        ce_details = {
            "survey": self.eq_survey_dates,
            "collection_exercise": self.collection_exercises[0],
            "collection_instruments": eq_cis,
            "events": {},
            "sample_summary": {},
            "sampleSize": 0,
            "sampleLinks": [],
        }

        return ce_details
