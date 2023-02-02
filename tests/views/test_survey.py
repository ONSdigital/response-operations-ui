import copy
import json
import os
from contextlib import suppress
from unittest.mock import MagicMock

import fakeredis
import jwt
import requests_mock
from requests import RequestException

from config import TestingConfig
from response_operations_ui.controllers.survey_controllers import (
    get_survey_short_name_by_id,
)
from response_operations_ui.views.surveys import _sort_collection_exercise
from tests.views import ViewTestCase
from tests.views.test_admin import url_permission_url, url_sign_in_data

collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
collection_exercise_event_id = "b4a36392-a21f-485b-9dc4-d151a8fcd565"
sample_summary_id = "b9487b59-2ac7-4fbf-b734-5a4c260ff235"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"

url_get_survey_list = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"
url_get_legal_basis_list = f"{TestingConfig.SURVEY_URL}/legal-bases"
url_create_survey = f"{TestingConfig.SURVEY_URL}/surveys"
url_get_survey_by_short_name = f"{TestingConfig.SURVEY_URL}/surveys/shortname/bres"
url_get_survey_by_qbs = f"{TestingConfig.SURVEY_URL}/surveys/shortname/QBS"
url_update_survey_details = f"{TestingConfig.SURVEY_URL}/surveys/ref/222"
project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/survey/survey_list.json") as f:
    survey_list = json.load(f)
with open(f"{project_root}/test_data/survey/legal_basis_list.json") as f:
    legal_basis_list = json.load(f)
with open(f"{project_root}/test_data/survey/survey.json") as f:
    survey_info = json.load(f)
with open(f"{project_root}/test_data/survey/survey_states.json") as f:
    survey_info_states = json.load(f)
with open(f"{project_root}/test_data/survey/updated_survey_list.json") as f:
    updated_survey_list = json.load(f)
with open(f"{project_root}/test_data/survey/create_survey_response.json") as f:
    create_survey_response = json.load(f)
url_get_collection_exercises = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey/{survey_info["survey"]["id"]}'
)
url_get_collection_exercises_link = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/link/{collection_exercise_id}"
)
url_get_sample_summary = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}"

url_get_eq_ci_selectors = (
    f"{TestingConfig.COLLECTION_INSTRUMENT_URL}"
    f"/collection-instrument-api/1.0.2/collectioninstrument?"
    f'searchString=%7B%22SURVEY_ID%22%3A+%22{survey_info["survey"]["id"]}%22%2C+%22TYPE%22%3A+%22EQ%22%7D'
)

url_post_instrument_link = (
    f"{TestingConfig.COLLECTION_INSTRUMENT_URL}"
    f'/collection-instrument-api/1.0.2/upload?survey_id={survey_info["survey"]["id"]}&'
    f"classifiers=%7B%22form_type%22%3A%220001%22%2C%22eq_id%22%3A%22qbs%22%7D"
)

user_permission_surveys_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "surveys.edit", "type": "DIRECT"}],
}


def sign_in_with_permission(self, mock_request, permission):
    mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
    mock_request.get(url_permission_url, json=permission, status_code=200)
    self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})


class TestSurvey(ViewTestCase):
    def setup_data(self):
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221",
            "surveyMode": "SEFT",
        }
        self.collection_exercises = [
            {
                "id": collection_exercise_id,
                "name": "201601",
                "exerciseRef": "201803",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
                "state": "PUBLISHED",
                "events": [
                    {
                        "id": "95525070-d117-4491-b149-0d6ef6b94562",
                        "collectionExerciseId": collection_exercise_id,
                        "tag": "go_live",
                        "timestamp": "2023-01-01T09:00:00.000Z",
                        "eventStatus": "RETRY",
                    },
                    {
                        "id": "689467d2-3d5a-4c34-bdb2-de02c633d0c2",
                        "collectionExerciseId": collection_exercise_id,
                        "tag": "mps",
                        "timestamp": "2023-01-01T07:00:00.000Z",
                        "eventStatus": "FAILED",
                    },
                    {
                        "id": "af35bdb9-70b7-283c-8ee0-4b0584b88634",
                        "collectionExerciseId": collection_exercise_id,
                        "tag": "reminder",
                        "timestamp": "2023-02-01T07:00:00.000Z",
                        "eventStatus": "PROCESSING",
                    },
                    {
                        "id": "f464e681-0b3a-f35f-604d-a6c3b2bb9b56",
                        "collectionExerciseId": collection_exercise_id,
                        "tag": "reminder2",
                        "timestamp": "2023-03-01T07:00:00.000Z",
                        "eventStatus": "SCHEDULED",
                    },
                ],
            }
        ]
        self.collection_exercises_link = [sample_summary_id]
        self.sample_summary = {
            "id": sample_summary_id,
            "effectiveStartDateTime": "",
            "effectiveEndDateTime": "",
            "surveyRef": "",
            "ingestDateTime": "2018-03-14T14:29:51.325Z",
            "state": "ACTIVE",
            "totalSampleUnits": 5,
            "expectedCollectionInstruments": 1,
        }
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

    @requests_mock.mock()
    def test_survey_list(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_surveys_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        response = self.client.get("/surveys")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)
        self.assertIn("Create survey".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_no_surveys(self, mock_request):
        mock_request.get(url_get_survey_list, status_code=204)

        response = self.client.get("/surveys")

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_list_fail(self, mock_request):
        mock_request.get(url_get_survey_list, status_code=500)

        response = self.client.get("/surveys")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_survey_list_connection_error(self, mock_request):
        mock_request.get(url_get_survey_list, exc=RequestException(request=MagicMock()))

        response = self.client.get("/surveys", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_survey_view(self, mock_request):
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info["survey"])

        response = self.client.get("/surveys/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_view_collection_exercise_event_status(self, mock_request):
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info["survey"])

        # When the exercise isn't live, nothing shows
        response = self.client.get("/surveys/bres", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Processing".encode(), response.data)

        # When the exercise is live, it shows a status.  Prioritises 'Processing' when multiple happen because that's
        # how the 'get_collex_event_status' function works
        exercise_copy = copy.deepcopy(self.collection_exercises)
        exercise_copy[0]["state"] = "LIVE"
        mock_request.get(url_get_collection_exercises, json=exercise_copy)
        response = self.client.get("/surveys/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Processing".encode(), response.data)

    @requests_mock.mock()
    def test_survey_view_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.client.get("/surveys/bres")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_survey_state_mapping(self, mock_request):
        mock_request.get(url_get_collection_exercises, json=survey_info_states["collection_exercises"])
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info_states["survey"])

        response = self.client.get("/surveys/bres")

        self.assertIn(b"Created", response.data)
        self.assertIn(b"Scheduled", response.data)
        self.assertIn(b"Ready for review", response.data)
        self.assertIn(b"Ready for live", response.data)
        self.assertIn(b"Live", response.data)
        self.assertIn(b"Ended", response.data)

    @requests_mock.mock()
    def test_get_survey_short_name_by_id(self, mock_request):
        with self.app.app_context():
            mock_request.get(url_get_survey_list, json=survey_list)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_is_cached(self, mock_request):
        with self.app.app_context():
            mock_request.get(url_get_survey_list, json=survey_list)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

            mock_request.get(url_get_survey_list, status_code=500)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_for_new_survey_id(self, mock_request):
        with self.app.app_context():
            mock_request.get(url_get_survey_list, json=survey_list)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

            mock_request.get(
                url_get_survey_list, json=[{"shortName": "NEW", "id": "a_new_survey_id", "surveyRef": "999"}]
            )
            self.assertEqual(get_survey_short_name_by_id("a_new_survey_id"), "NEW")

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_when_get_list_fails(self, mock_request):
        # Delete any existing survey cache
        with suppress(AttributeError):
            del self.app.surveys_dict

        with self.app.app_context():
            # API error on first attempt
            mock_request.get(url_get_survey_list, status_code=500)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), None)

            # Successfully retrieve surveys
            mock_request.get(url_get_survey_list, json=survey_list)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

            # API error trying to fetch new survey
            mock_request.get(url_get_survey_list, status_code=500)
            self.assertEqual(get_survey_short_name_by_id("a_new_survey_id1234567890"), None)

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_when_id_not_found(self, mock_request):
        with self.app.app_context():
            mock_request.get(url_get_survey_list, json=survey_list)
            self.assertEqual(get_survey_short_name_by_id("not_a_valid_survey_id"), None)

            # Check cached dictionary is preserved
            mock_request.get(url_get_survey_list, status_code=500)
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")
            self.assertEqual(get_survey_short_name_by_id("not_a_valid_survey_id"), None)

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_fdi_surveys(self, mock_request):
        with self.app.app_context():
            mock_request.get(url_get_survey_list, json=survey_list)

            self.assertEqual(get_survey_short_name_by_id("QOFDI_id"), "FDI")
            self.assertEqual(get_survey_short_name_by_id("QIFDI_id"), "FDI")
            self.assertEqual(get_survey_short_name_by_id("AOFDI_id"), "FDI")
            self.assertEqual(get_survey_short_name_by_id("AIFDI_id"), "FDI")
            self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

    @requests_mock.mock(real_http=True)
    def test_update_survey_details_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_survey_details = {
            "hidden_survey_ref": "222",
            "long_name": "New Survey Long Name",
            "short_name": "QBX",
            "survey_mode": "EQ",
        }
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        response = self.client.post(
            "/surveys/edit-survey-details/QBS", data=changed_survey_details, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("New Survey Long Name".encode(), response.data)
        self.assertIn("QBX".encode(), response.data)
        self.assertIn("EQ".encode(), response.data)

    @requests_mock.mock()
    def test_update_survey_details_failure(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_survey_details = {
            "hidden_survey_ref": "222",
            "long_name": "New Survey Long Name",
            "short_name": "QBX",
            "survey_mode": "EQ",
        }
        mock_request.put(url_update_survey_details, status_code=500)

        response = self.client.post("/surveys/edit-survey-details/QBS", data=changed_survey_details)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_survey_details_failed_validation(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_survey_details = {
            "hidden_survey_ref": "222",
            "long_name": "New Survey Long Name",
            "short_name": "Q BX",
            "survey_mode": "EQ",
        }
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_qbs, json=survey_info["survey"])

        response = self.client.post(
            "/surveys/edit-survey-details/QBS", data=changed_survey_details, follow_redirects=True
        )
        self.assertIn("Error updating survey details".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_survey_details(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.get(url_get_survey_by_short_name, json=survey_info["survey"])

        response = self.client.get("surveys/edit-survey-details/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("221".encode(), response.data)

    @requests_mock.mock()
    def test_get_survey_create(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)

        response = self.client.get("surveys/create")

        self.assertEqual(response.status_code, 200)

        # Check form fields all present and correct
        self.assertIn('id="survey_ref"'.encode(), response.data)
        self.assertIn('id="long_name"'.encode(), response.data)
        self.assertIn('id="short_name"'.encode(), response.data)
        self.assertIn('id="legal_basis"'.encode(), response.data)

        # Check legal bases populated - slightly brittle but these really don't change very often
        self.assertIn('"STA1947"'.encode(), response.data)
        self.assertIn('"GovERD"'.encode(), response.data)
        self.assertIn('"Vol"'.encode(), response.data)
        self.assertIn('"STA1947_BEIS"'.encode(), response.data)
        self.assertIn('"Vol_BEIS"'.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_ok(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947",
            "survey_mode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        expected_survey_request = {
            "surveyRef": "999",
            "shortName": "TEST",
            "longName": "Test Survey",
            "legalBasisRef": "STA1947",
            "surveyType": "Business",
            "surveyMode": "SEFT",
            "classifiers": [
                {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["FORM_TYPE"]},
                {"name": "COMMUNICATION_TEMPLATE", "classifierTypes": ["LEGAL_BASIS", "REGION"]},
            ],
            "eqVersion": "",
        }
        mock_request.post(
            url_create_survey, additional_matcher=lambda req: req.json() == expected_survey_request, status_code=201
        )
        mock_request.get(url_get_survey_list, json=updated_survey_list)

        response = self.client.post("surveys/create", data=create_survey_request, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Survey</a> has been added".encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_conflict(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        error_message = "XXX ERROR MESSAGE XXX"
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947",
            "survey_mode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, text=error_message, status_code=409)

        response = self.client.post("surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check for error message
        self.assertIn(error_message.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_bad_request(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        error_message = "XXX ERROR MESSAGE XXX"
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947",
            "survey_mode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, text=error_message, status_code=400)

        response = self.client.post("surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check for error message
        self.assertIn(error_message.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_bad_survey_ref(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_survey_request = {
            "survey_ref": "BAD!",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947",
            "surveyMode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, json=create_survey_response, status_code=201)

        response = self.client.post("surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check error div is present
        self.assertIn('id="save-error"'.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_spaces_shortname(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TE ST",
            "legal_basis": "STA1947",
            "surveyMode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, json=create_survey_response, status_code=201)

        response = self.client.post("surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check error div is present
        self.assertIn('id="save-error"'.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_html_shortname(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "<b>TEST</b>",
            "legal_basis": "STA1947",
            "surveyMode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, json=create_survey_response, status_code=201)

        response = self.client.post("surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check error div is present
        self.assertIn('id="save-error"'.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_html_longname(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "<b>Test Survey</b>",
            "short_name": "TEST",
            "legal_basis": "STA1947",
            "surveyMode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, json=create_survey_response, status_code=201)

        response = self.client.post("surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check error div is present
        self.assertIn('id="save-error"'.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_internal_server_error(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947",
            "survey_mode": "SEFT",
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, text="Internal server error", status_code=500)

        response = self.client.post("surveys/create", data=create_survey_request)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_survey_details_failed_validation_short_name_has_spaces(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_survey_details = {
            "hidden_survey_ref": "222",
            "long_name": "New Survey Long Name",
            "short_name": "QBX spaces",
            "survey_mode": "EQ",
        }
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        mock_request.get(url_get_survey_by_short_name, json=survey_info["survey"])

        response = self.client.post(
            "/surveys/edit-survey-details/bres", data=changed_survey_details, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error updating survey details".encode(), response.data)

    def test_sort_collection_exercise(self):
        # Given there are collection exercises loaded for a survey
        with open(f"{project_root}/test_data/survey/multiple_ces.json") as f:
            collection_exercises = json.load(f)

        # When collection exercises are sorted
        _sort_collection_exercise(collection_exercises)

        # Then CEs should be in order by mps date
        # And CEs without mps date should be at the end
        ce_ids_in_order = [ce["id"] for ce in collection_exercises]
        self.assertEqual(
            ce_ids_in_order,
            [
                "48b6c58a-bf5b-4bb3-8d7d-5e205ff3a0fd",
                "9f9d28c6-d010-47cc-832c-6ab9b741ee96",
                "23a83a62-87dd-4c6c-97e2-4b207f7e57f5",
                "bd4d2bec-28d3-421c-a399-b2840e52e36e",
            ],
        )

    def test_format_shortname(self):
        from response_operations_ui.common.mappers import format_short_name

        self.assertEqual(format_short_name("QBS"), "QBS")
        self.assertEqual(format_short_name("Sand&Gravel"), "Sand & Gravel")

    @requests_mock.mock()
    def test_link_collection_instrument_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_survey_details = {"formtype": "0001"}
        data = [
            {
                "classifiers": {"COLLECTION_EXERCISE": [], "RU_REF": [], "eq_id": "qbs", "form_type": "0001"},
                "file_name": "0001",
                "id": "dde9cab1-b5bd-42a2-8ff7-80e3ddb8c11e",
                "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            }
        ]
        mock_request.get(url_get_survey_by_qbs, json=survey_info["survey"])
        mock_request.get(url_get_eq_ci_selectors, json=data)
        mock_request.post(url_post_instrument_link)
        response = self.client.post("/surveys/QBS/link-collection-instrument", data=changed_survey_details)
        self.assertEqual(response.status_code, 200)
        self.assertIn("0001".encode(), response.data)

    @requests_mock.mock()
    def test_link_collection_instrument_duplicate(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_survey_details = {"formtype": "0001"}
        data = [
            {
                "classifiers": {"COLLECTION_EXERCISE": [], "RU_REF": [], "eq_id": "qbs", "form_type": "0001"},
                "file_name": "0001",
                "id": "dde9cab1-b5bd-42a2-8ff7-80e3ddb8c11e",
                "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            }
        ]
        error_data = {"errors": ["Cannot upload an instrument with an identical set of classifiers"]}
        mock_request.get(url_get_survey_by_qbs, json=survey_info["survey"])
        mock_request.get(url_get_eq_ci_selectors, json=data)
        mock_request.post(url_post_instrument_link, status_code=400, json=error_data)
        response = self.client.post("/surveys/QBS/link-collection-instrument", data=changed_survey_details)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This page has 1 error".encode(), response.data)
        self.assertIn("Cannot upload an instrument with an identical set of classifiers".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_edit_permission(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_surveys_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        response = self.client.get("/surveys")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)
        self.assertIn("Edit survey".encode(), response.data)
        self.assertIn("Create survey".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_no_edit_permission(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.client.get("/surveys")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)
        self.assertNotIn("Edit survey".encode(), response.data)
        self.assertNotIn("Create survey".encode(), response.data)

    @requests_mock.mock()
    def test_survey_view_edit_permission(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_surveys_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info["survey"])

        response = self.client.get("/surveys/bres", follow_redirects=True)

        self.assertIn("Create collection exercise".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_view_no_edit_permission(self, mock_request):
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info["survey"])

        response = self.client.get("/surveys/bres", follow_redirects=True)

        self.assertNotIn("Link collection instrument".encode(), response.data)
        self.assertNotIn("Create collection exercise".encode(), response.data)
        self.assertEqual(response.status_code, 200)
