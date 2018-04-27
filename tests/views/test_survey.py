from contextlib import suppress
import json
import unittest
from unittest.mock import MagicMock

from requests import RequestException
import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.survey_controllers import get_survey_short_name_by_id

url_get_survey_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/surveys'
with open('tests/test_data/survey/survey_list.json') as json_data:
    survey_list = json.load(json_data)
url_get_survey_by_short_name = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname/bres'
with open('tests/test_data/survey/survey.json') as json_data:
    survey_info = json.load(json_data)
with open('tests/test_data/survey/survey_states.json') as json_data:
    survey_info_states = json.load(json_data)
url_update_survey_details = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/edit-survey-details/222'
with open('tests/test_data/survey/updated_survey_list.json') as json_data:
    updated_survey_list = json.load(json_data)


class TestSurvey(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    @requests_mock.mock()
    def test_home(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("View list of business surveys".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.app.get("/surveys")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_fail(self, mock_request):
        mock_request.get(url_get_survey_list, status_code=500)

        response = self.app.get("/surveys", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_connection_error(self, mock_request):
        mock_request.get(url_get_survey_list, exc=RequestException(request=MagicMock()))

        response = self.app.get("/surveys", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_survey_view(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey_info)

        response = self.app.get("/surveys/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_view_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.app.get("/surveys/bres", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_survey_state_mapping(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey_info_states)

        response = self.app.get("/surveys/bres")
        self.assertIn(b'Created', response.data)
        self.assertIn(b'Scheduled', response.data)
        self.assertIn(b'Ready for review', response.data)
        self.assertIn(b'Ready for live', response.data)
        self.assertIn(b'Live', response.data)

    @requests_mock.mock()
    def test_get_survey_short_name_by_id(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_is_cached(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

        mock_request.get(url_get_survey_list, status_code=500)
        self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_for_new_survey_id(self, mock_request):
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
            del app.surveys_dict

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
        mock_request.get(url_get_survey_list, json=survey_list)
        self.assertEqual(get_survey_short_name_by_id("not_a_valid_survey_id"), None)

        # Check cached dictionary is preserved
        mock_request.get(url_get_survey_list, status_code=500)
        self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")
        self.assertEqual(get_survey_short_name_by_id("not_a_valid_survey_id"), None)

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_fdi_surveys(self, mock_request):
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
        response = self.app.post(f"/surveys/edit-survey-details/QBS", data=changed_survey_details,
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
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.put(url_update_survey_details, status_code=500)
        mock_request.get(url_get_survey_list, json=updated_survey_list)
        response = self.app.post(f"/surveys/edit-survey-details/QBS", data=changed_survey_details,
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_survey_details(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        mock_request.get(url_get_survey_by_short_name, json=survey_info)
        response = self.app.get(f"surveys/edit-survey-details/bres", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("221".encode(), response.data)

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
        mock_request.get(url_get_survey_by_short_name, json=survey_info)
        response = self.app.post(f"/surveys/edit-survey-details/bres", data=changed_survey_details,
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Error updating survey details".encode(), response.data)
