import json
from contextlib import suppress
from unittest.mock import MagicMock

import requests_mock
from requests import RequestException

from config import TestingConfig
from response_operations_ui.controllers.survey_controllers import get_survey_short_name_by_id
from response_operations_ui.views.surveys import _sort_collection_exercise
from tests.views import ViewTestCase


collection_exercise_id = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
collection_exercise_event_id = 'b4a36392-a21f-485b-9dc4-d151a8fcd565'
sample_summary_id = 'b9487b59-2ac7-4fbf-b734-5a4c260ff235'
survey_id = 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87'

url_get_survey_list = f'{TestingConfig.SURVEY_URL}/surveys/surveytype/Business'
url_get_legal_basis_list = f'{TestingConfig.SURVEY_URL}/legal-bases'
url_create_survey = f'{TestingConfig.SURVEY_URL}/surveys'

with open('tests/test_data/survey/survey_list.json') as f:
    survey_list = json.load(f)
with open('tests/test_data/survey/legal_basis_list.json') as f:
    legal_basis_list = json.load(f)

url_get_survey_by_short_name = f'{TestingConfig.SURVEY_URL}/surveys/shortname/bres'
url_get_survey_by_qbs = f'{TestingConfig.SURVEY_URL}/surveys/shortname/QBS'
with open('tests/test_data/survey/survey.json') as f:
    survey_info = json.load(f)
with open('tests/test_data/survey/survey_states.json') as f:
    survey_info_states = json.load(f)
url_update_survey_details = f'{TestingConfig.SURVEY_URL}/surveys/ref/222'
with open('tests/test_data/survey/updated_survey_list.json') as f:
    updated_survey_list = json.load(f)
with open('tests/test_data/survey/create_survey_response.json') as f:
    create_survey_response = json.load(f)
url_get_collection_exercises = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
    f'/collectionexercises/survey/{survey_info["survey"]["id"]}'
)
url_get_collection_exercise_events = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
    f'/collectionexercises/{collection_exercise_id}/events'
)
url_get_collection_exercises_link = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
    f'/collectionexercises/link/{collection_exercise_id}'
)
url_get_sample_summary = (
    f'{TestingConfig.SAMPLE_URL}'
    f'/samples/samplesummary/{sample_summary_id}'
)


class TestSurvey(ViewTestCase):

    def setup_data(self):
        self.survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221"
        }
        self.collection_exercises = [
            {
                "id": collection_exercise_id,
                "name": "201601",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
                "state": "PUBLISHED"
            }
        ]
        self.collection_exercises_events = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "mps",
                "timestamp": "2018-03-16T00:00:00.000Z"
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
            "expectedCollectionInstruments": 1
        }

    @requests_mock.mock()
    def test_home(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("View list of business surveys".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.client.get("/surveys")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)

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
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info['survey'])

        response = self.client.get("/surveys/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_view_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.client.get("/surveys/bres")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_survey_state_mapping(self, mock_request):
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises, json=survey_info_states['collection_exercises'])
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_short_name, json=survey_info_states['survey'])

        response = self.client.get("/surveys/bres")

        self.assertIn(b'Created', response.data)
        self.assertIn(b'Scheduled', response.data)
        self.assertIn(b'Ready for review', response.data)
        self.assertIn(b'Ready for live', response.data)
        self.assertIn(b'Live', response.data)

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

            mock_request.get(url_get_survey_list, json=[{"shortName": "NEW",
                                                         "id": "a_new_survey_id",
                                                         "surveyRef": "999"}])
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

    @requests_mock.mock()
    def test_update_survey_details_success(self, mock_request):
        changed_survey_details = {
            "hidden_survey_ref": '222',
            "long_name": 'New Survey Long Name',
            "short_name": 'QBX'
        }
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        response = self.client.post(f"/surveys/edit-survey-details/QBS", data=changed_survey_details,
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('New Survey Long Name'.encode(), response.data)
        self.assertIn('QBX'.encode(), response.data)

    @requests_mock.mock()
    def test_update_survey_details_failure(self, mock_request):
        changed_survey_details = {
            "hidden_survey_ref": '222',
            "long_name": 'New Survey Long Name',
            "short_name": 'QBX'
        }
        mock_request.put(url_update_survey_details, status_code=500)

        response = self.client.post(f"/surveys/edit-survey-details/QBS", data=changed_survey_details)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_survey_details_failed_validation(self, mock_request):
        changed_survey_details = {
            "hidden_survey_ref": '222',
            "long_name": 'New Survey Long Name',
            "short_name": 'Q BX'
        }
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_survey_by_qbs, json=survey_info['survey'])

        response = self.client.post(f"/surveys/edit-survey-details/QBS", data=changed_survey_details,
                                    follow_redirects=True)
        self.assertIn("Error updating survey details".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_survey_details(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.get(url_get_survey_by_short_name, json=survey_info['survey'])

        response = self.client.get(f"surveys/edit-survey-details/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("221".encode(), response.data)

    @requests_mock.mock()
    def test_get_survey_create(self, mock_request):
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)

        response = self.client.get(f"surveys/create")

        self.assertEqual(response.status_code, 200)

        # Check form fields all present and correct
        self.assertIn("id=\"survey_ref\"".encode(), response.data)
        self.assertIn("id=\"long_name\"".encode(), response.data)
        self.assertIn("id=\"short_name\"".encode(), response.data)
        self.assertIn("id=\"legal_basis\"".encode(), response.data)

        # Check legal bases populated - slightly brittle but these really don't change very often
        self.assertIn("\"STA1947\"".encode(), response.data)
        self.assertIn("\"GovERD\"".encode(), response.data)
        self.assertIn("\"Vol\"".encode(), response.data)
        self.assertIn("\"STA1947_BEIS\"".encode(), response.data)
        self.assertIn("\"Vol_BEIS\"".encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_ok(self, mock_request):
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947"
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        expected_survey_request = {
            "surveyRef": "999",
            "shortName": "TEST",
            "longName": "Test Survey",
            "legalBasisRef": "STA1947",
            "surveyType": 'Business',
            "classifiers": [
                {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["FORM_TYPE"]},
                {"name": "COMMUNICATION_TEMPLATE", "classifierTypes": ["LEGAL_BASIS", "REGION"]}
            ]
        }
        mock_request.post(url_create_survey, additional_matcher=lambda req: req.json() == expected_survey_request,
                          status_code=201)
        mock_request.get(url_get_survey_list, json=updated_survey_list)

        response = self.client.post(f"surveys/create", data=create_survey_request, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_survey_conflict(self, mock_request):
        error_message = "XXX ERROR MESSAGE XXX"
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947"
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, text=error_message, status_code=409)

        response = self.client.post(f"surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check for error message
        self.assertIn(error_message.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_bad_request(self, mock_request):
        error_message = "XXX ERROR MESSAGE XXX"
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947"
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, text=error_message, status_code=400)

        response = self.client.post(f"surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check for error message
        self.assertIn(error_message.encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_bad_survey_ref(self, mock_request):
        create_survey_request = {
            "survey_ref": "BAD!",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947"
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, json=create_survey_response, status_code=201)

        response = self.client.post(f"surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check error div is present
        self.assertIn("id=\"save-error\"".encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_bad_shortname(self, mock_request):
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TE ST",
            "legal_basis": "STA1947"
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, json=create_survey_response, status_code=201)

        response = self.client.post(f"surveys/create", data=create_survey_request)

        self.assertEqual(response.status_code, 200)

        # Check error div is present
        self.assertIn("id=\"save-error\"".encode(), response.data)

    @requests_mock.mock()
    def test_create_survey_internal_server_error(self, mock_request):
        create_survey_request = {
            "survey_ref": "999",
            "long_name": "Test Survey",
            "short_name": "TEST",
            "legal_basis": "STA1947"
        }
        mock_request.get(url_get_legal_basis_list, json=legal_basis_list)
        mock_request.post(url_create_survey, text="Internal server error", status_code=500)

        response = self.client.post(f"surveys/create", data=create_survey_request)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_survey_details_failed_validation_short_name_has_spaces(self, mock_request):
        changed_survey_details = {
            "hidden_survey_ref": '222',
            "long_name": 'New Survey Long Name',
            "short_name": 'QBX spaces'
        }
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        mock_request.get(url_get_survey_by_short_name, json=survey_info['survey'])

        response = self.client.post(f"/surveys/edit-survey-details/bres", data=changed_survey_details,
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error updating survey details".encode(), response.data)

    def test_sort_collection_exercise(self):
        # Given there are collection exercises loaded for a survey
        with open('tests/test_data/survey/multiple_ces.json') as f:
            collection_exercises = json.load(f)

        # When collection exercises are sorted
        _sort_collection_exercise(collection_exercises)

        # Then CEs should be in order by mps date
        # And CEs without mps date should be at the end
        ce_ids_in_order = [ce['id'] for ce in collection_exercises]
        self.assertEqual(ce_ids_in_order, ['bd4d2bec-28d3-421c-a399-b2840e52e36e',
                                           '23a83a62-87dd-4c6c-97e2-4b207f7e57f5',
                                           '9f9d28c6-d010-47cc-832c-6ab9b741ee96',
                                           '48b6c58a-bf5b-4bb3-8d7d-5e205ff3a0fd'])

    def test_format_shortname(self):
        from response_operations_ui.common.mappers import format_short_name

        self.assertEqual(format_short_name('QBS'), 'QBS')
        self.assertEqual(format_short_name('Sand&Gravel'), 'Sand & Gravel')
