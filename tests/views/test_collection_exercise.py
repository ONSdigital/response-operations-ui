import json
import os
from io import BytesIO
from unittest.mock import patch
from urllib.parse import urlencode, urlparse

import jwt
import mock
import requests_mock

from config import TestingConfig
from response_operations_ui.views.collection_exercise import (
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
period = "000000"
sample_summary_id = "1a11543f-eb19-41f5-825f-e41aca15e724"
short_name = "MBS"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_ref = "141"

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

with open(failed_validation) as json_data:
    collection_exercise_details_failedvalidation = json.load(json_data)

with open(f"{project_root}/test_data/survey/edited_survey_ce_details.json") as json_data:
    updated_survey_info = json.load(json_data)

with open(f"{project_root}/test_data/survey/survey_by_id.json") as fp:
    survey_by_id = json.load(fp)

with open(f"{project_root}/test_data/collection_exercise/exercise_data.json") as json_data:
    exercise_data = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/ce_details_new_event.json") as fp:
    ce_details_no_events = json.load(fp)

with open(f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details.json") as fp:
    formatted_collection_exercise_details = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/formatted_new_collection_exercise_details.json") as fp:
    formatted_new_collection_exercise_details = json.load(fp)

with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details.json") as seft:
    seft_collection_exercise_details = json.load(seft)
with open(
    f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details_set_ready_for_live.json"
) as seft:
    seft_collection_exercise_details_set_ready_for_live = json.load(seft)
with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details_ready_for_live.json") as seft:
    seft_collection_exercise_details_ready_for_live = json.load(seft)
with open(
    f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details_execution_started.json"
) as seft:
    seft_collection_exercise_details_execution_started = json.load(seft)
with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details_validated.json") as seft:
    seft_collection_exercise_details_validated = json.load(seft)
with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details_executed.json") as seft:
    seft_collection_exercise_details_executed = json.load(seft)
with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details_ended.json") as seft:
    seft_collection_exercise_details_ended = json.load(seft)

with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as json_data:
    collection_exercise = json.load(json_data)

with open(f"{project_root}/test_data/survey/single_survey.json") as json_data:
    survey = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/events.json") as json_data:
    events = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/nudge_events_one.json") as json_data:
    nudge_events_one = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/nudge_events_two.json") as json_data:
    nudge_events_two = json.load(json_data)

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

user_permission_surveys_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "surveys.edit", "type": "DIRECT"}],
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
url_update_ce_eq_version = f"{collection_exercise_root}/{collection_exercise_id}/eqVersion"
url_update_ce_period = f"{collection_exercise_root}/{collection_exercise_id}/exerciseRef"
url_get_collection_exercise_events = f"{collection_exercise_root}/{collection_exercise_id}/events"
url_create_collection_exercise = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_execute = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexerciseexecution/{collection_exercise_id}"
url_get_by_survey_with_ref_end_date = f"{collection_exercise_root}/survey/{short_name}/{period}/event/ref_period_end?"

collection_instrument_root = f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2"
url_collection_instrument = f"{collection_instrument_root}/upload/{collection_exercise_id}"
url_collection_instrument_link = (
    f"{collection_instrument_root}/link-exercise/{collection_instrument_id}/{collection_exercise_id}"
)
url_collection_instrument_unlink = (
    f"{collection_instrument_root}/unlink-exercise/{collection_instrument_id}/{collection_exercise_id}"
)

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

url_get_by_survey_with_ref_start_date = (
    f"{collection_exercise_root}/survey/{short_name}/{period}/event/ref_period_start?"
)

url_party_delete_attributes = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/attributes/sample-summary/{sample_summary_id}"
)

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
        self.survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221",
            "eqVersion": "",
            "surveyMode": "SEFT",
        }
        self.seft_survey = {
            "id": survey_id,
            "longName": "Monthly Survey of Building Materials Bricks",
            "shortName": "Bricks",
            "surveyRef": "074",
            "eqVersion": "",
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
        self.survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221",
            "eqVersion": "",
            "surveyMode": "SEFT",
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
            }
        ]
        self.collection_exercises_link = [sample_summary_id]
        self.collection_instruments = [
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
            }
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
                    "COLLECTION_EXERCISE": [],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                },
                "file_name": None,
                "id": collection_instrument_id,
                "surveyId": survey_id,
            }
        ]
        self.linked_sample = {
            "collectionExerciseId": collection_exercise_id,
            "sampleSummaryIds": [
                sample_summary_id,
            ],
        }
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

    @requests_mock.mock()
    def test_collection_exercise_view_eq_non_ref_date(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_eq_ref_start_date(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_start_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_eq_ref_end_date(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_end_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_eq_both_ref_dates(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_seft(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
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
        self.assertNotIn("Select eQ version".encode(), response.data)
        self.assertNotIn("Set ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_set_ready_for_live(self, mock_request, mock_details):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        post_data = {"ciFile": (BytesIO(b"data"), "074_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_details.return_value = seft_collection_exercise_details_set_ready_for_live

        response = self.client.get(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_ready_for_live(self, mock_request, mock_details):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        post_data = {"ciFile": (BytesIO(b"data"), "074_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_details.return_value = seft_collection_exercise_details_ready_for_live

        response = self.client.get(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Ready for live".encode(), response.data)
        self.assertNotIn("Set ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_execution_started(self, mock_request, mock_details):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        post_data = {"ciFile": (BytesIO(b"data"), "074_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_details.return_value = seft_collection_exercise_details_execution_started

        response = self.client.get(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_validated(self, mock_request, mock_details):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        post_data = {"ciFile": (BytesIO(b"data"), "074_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_details.return_value = seft_collection_exercise_details_validated

        response = self.client.get(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_executed(self, mock_request, mock_details):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        post_data = {"ciFile": (BytesIO(b"data"), "074_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_details.return_value = seft_collection_exercise_details_executed

        response = self.client.get(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_collection_exercise_view_seft_ended(self, mock_request, mock_details):
        mock_request.get(url_get_survey_by_short_name, json=self.seft_survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        post_data = {"ciFile": (BytesIO(b"data"), "074_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_details.return_value = seft_collection_exercise_details_ended

        response = self.client.get(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("074".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Ended".encode(), response.data)
        self.assertNotIn("Set ready for live".encode(), response.data)

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
        self.assertIn("Loading (5 / 10 loaded) &hellip;".encode(), response.data)
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
        self.assertIn("Loading &hellip;".encode(), response.data)
        self.assertIn("Refresh to see progress".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_survey_errors(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)

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
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.client.get(f"/surveys/{short_name}/{period}")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_ci_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", status_code=400)

        response = self.client.get(f"/surveys/{short_name}/{period}")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_collection_instrument(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
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
    def test_select_collection_instrument(self, mock_request, mock_details):
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-ci": ""}
        mock_request.post(url_collection_instrument_link, status_code=200)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instruments added".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_select_collection_instrument(self, mock_request, mock_details):
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-ci": ""}
        mock_request.post(url_collection_instrument_link, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to add collection instrument(s)".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_no_selected_collection_instrument(self, mock_request, mock_details):
        post_data = {"checkbox-answer": [], "ce_id": "000000", "select-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: No collection instruments selected".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_view_collection_instrument_after_upload(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_upload_collection_instrument(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_collection_instrument_when_bad_extension(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Wrong file type for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_collection_instrument_when_bad_form_type_format(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_collection_instrument_bad_file_name_format(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_collection_instrument_form_type_not_integer(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_collection_instrument_when_no_file(self, mock_request, mock_details):
        post_data = {"load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_view_collection_instrument(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_add_another_collection_instrument_when_already_uploaded_no_permission(self, mock_request, mock_details):
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
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

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
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}
        sample_data = {"id": sample_summary_id}
        collection_exercise_link = {"id": ""}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=200, json=sample_data)
        mock_request.put(url_collection_exercise_link, status_code=500, json=collection_exercise_link)

        response = self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 4)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_sample_exception(self, mock_request, mock_details):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}
        sample_data = {"id": sample_summary_id}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=500, json=sample_data)

        response = self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_upload_sample(self, mock_request, mock_details):
        data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_no_upload_sample_when_bad_extension(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        data = {"sampleFile": (BytesIO(b"data"), "test.html"), "load-sample": ""}
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
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

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
    def test_eq_version_change_success(self, mock_request, mock_details):
        data = {"eq-version": "v3"}
        with open(
            f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details_eq_version.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)
        mock_request.put(url_update_ce_eq_version, status_code=200)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        response = self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("eQ version updated to v3".encode(), response.data)

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

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_get_processing(self, mock_request, mock_details):
        details = formatted_collection_exercise_details.copy()
        details["collection_exercise"]["state"] = "EXECUTION_STARTED"
        mock_details.return_value = details

        response = self.client.get(f"/surveys/{short_name}/{period}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_execution(self, mock_request, mock_details):
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
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_update_collection_exercise_details_success(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",
            "hidden_survey_id": survey_id,
        }
        # update survey
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.put(url_update_ce_user_details)
        mock_request.put(url_update_ce_period)
        # redirect to survey details
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("16th June 2019".encode(), response.data)
        self.assertIn("201906".encode(), response.data)

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
            f"/surveys/{short_name}/201906/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f"/surveys/{short_name}")

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
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details", data=changed_ce_details
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
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details", data=changed_ce_details
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
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 7)
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
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 7)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_get_ce_details(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details", follow_redirects=True
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
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_failed_unlink_collection_instrument(self, mock_request, mock_details):
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-ci": "",
        }

        mock_request.put(url_collection_instrument_unlink, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "123456",
        }
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("123456".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_failure(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "123456",
        }
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.post(url_create_collection_exercise, status_code=500)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", data=new_collection_exercise_details
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_create_ce_form(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        response = self.client.get(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_failed_create_ce_validation_period_exists(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        taken_period = "12345"
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": taken_period,
        }
        ces = self.collection_exercises
        ces[0]["exerciseRef"] = taken_period
        mock_request.get(url_ces_by_survey, json=ces)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.post(url_create_collection_exercise, status_code=200)

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
    def test_failed_create_ce_letters_fails_in_period_validation(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "hello",
        }
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

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
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
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
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
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
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Schedule nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_schedule_nudge_email_option_present(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_can_create_up_to_five_nudge_email(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=nudge_events_two)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

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
            mock_request.get(url_get_collection_exercise_events, json=nudge_events_two)
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
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Replace sample file".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_load_collection_instruments_is_not_present(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_details.return_value = seft_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Upload SEFT files".encode(), response.data)

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
        self.assertIn("Remove SEFT file".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_seft_upload_collection_instrument_supports_xls(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xls"), "load-ci": ""}
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
        self.assertIn("Remove SEFT file".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_seft_failed_upload_collection_instrument(self, mock_request, mock_details):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)

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

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Add".encode(), response.data)
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Add reminder".encode(), response.data)
        self.assertIn("Add nudge email".encode(), response.data)
        self.assertIn("Replace sample file & CI".encode(), response.data)

    @requests_mock.mock()
    def test_survey_edit_permission_collection_exercise_no_sample(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
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
        self.assertIn("Upload sample file & CI".encode(), response.data)

    @requests_mock.mock()
    def test_no_survey_edit_permission_collection_exercise(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("View sample file & CI".encode(), response.data)

    @requests_mock.mock()
    def test_seft_view_sample_ci_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details_no_sample["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("No sample file uploaded".encode(), response.data)
        self.assertIn("Upload sample file".encode(), response.data)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("Upload SEFT files".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_eq_view_sample_ci_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[""])
        mock_request.get(url_get_sample_summary, json="")

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("No sample file uploaded".encode(), response.data)
        self.assertIn("Upload sample file".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("checkbox-answer".encode(), response.data)
        self.assertIn("Select eQ version".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_eq_view_sample_ci_page_sample_load_count(self, mock_request, mock_details):
        sample_status_json = {"areAllSampleUnitsLoaded": False, "expectedTotal": 10, "currentTotal": 5}
        mock_details.return_value = ce_details_sample_init_state
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_sample_summary_status, json=sample_status_json)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?show_msg=true")

        self.assertEqual(200, response.status_code)
        self.assertIn("Loading sample (5 / 10 loaded) &hellip;".encode(), response.data)
        self.assertIn("Refresh to see progress".encode(), response.data)
        self.assertIn("Replace sample file".encode(), response.data)
        self.assertIn("eQ collection instruments available".encode(), response.data)
        self.assertIn("Select eQ version".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_eq_view_sample_ci_page_failed_sample_check(self, mock_request, mock_details):
        mock_details.return_value = ce_details_sample_init_state
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_sample_summary_status, status_code=500)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample summary check failed.  Refresh page to try again".encode(), response.data)
        self.assertIn("Refresh to see progress".encode(), response.data)
        self.assertIn("Replace sample file".encode(), response.data)
        self.assertIn("eQ collection instruments available".encode(), response.data)
        self.assertIn("Select eQ version".encode(), response.data)

    @requests_mock.mock()
    def test_loaded_sample_view_sample_ci_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertIn("Replace sample file".encode(), response.data)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("Upload SEFT files".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_seft_loaded_sample_view_sample_ci_page_no_survey_permission(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertNotIn("Replace sample file".encode(), response.data)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("View SEFT files".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_linked_ci_eq_view_sample_ci_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertIn("Replace sample file".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("unlink-ci-1".encode(), response.data)
        self.assertIn("Select eQ version".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_linked_ci_eq_view_sample_ci_page_no_survey_permission(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertNotIn("Replace sample file".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertNotIn("form-unselect-ci-1".encode(), response.data)
        self.assertIn("Select eQ version".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @requests_mock.mock()
    def test_loaded_sample_upload_sample_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
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
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_eq_both_ref_date["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_ref_both_date)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}", json=self.collection_instruments, complete_qs=True
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=self.eq_ci_selectors, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=collection_exercise_eq_ref_start_date)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=collection_exercise_eq_ref_end_date)

        response = self.client.get(f"/surveys/{short_name}/{period}/upload-sample-file")

        self.assertEqual(500, response.status_code)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_upload_sample_no_survey_permission(self, mock_request, mock_details):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

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

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_loaded_sample_no_survey_permission(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=204)
        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_loaded_ci_load_collection_instrument_no_page_survey_permission(self, mock_request, mock_details):
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
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
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_remove_ci_load_collection_instrument_page_no_survey_permission(self, mock_request, mock_details):
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-ci": "",
        }

        mock_request.put(url_collection_instrument_unlink, status_code=200)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_no_survey_edit_permission(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.eq_survey_dates)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Add".encode(), response.data)
        self.assertNotIn("Edit".encode(), response.data)
        self.assertNotIn("Add nudge email".encode(), response.data)
        self.assertNotIn("Add reminder".encode(), response.data)
        self.assertIn("Uploaded".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_manage_collection_instruments_is_present_no_edit_permission(self, mock_request, mock_details):
        mock_details.return_value = formatted_new_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(f"/surveys/{short_name}/{period}/", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Manage collection instruments".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    def test_load_collection_instruments_is_not_present_no_edit_permission(self, mock_request, mock_details):
        mock_details.return_value = seft_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info["survey"])
        mock_request.get(url_ces_by_survey, json=updated_survey_info["collection_exercises"])
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Load collection instruments".encode(), response.data)
