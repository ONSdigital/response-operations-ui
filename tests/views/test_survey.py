from contextlib import suppress
import json
import unittest
from unittest.mock import MagicMock

import requests_mock
from requests import RequestException

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

        response = self.app.get("/surveys/bres")

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

        mock_request.get(url_get_survey_list, json=[{"shortName": "NEW", "id": "a_new_survey_id"}])
        self.assertEqual(get_survey_short_name_by_id("a_new_survey_id"), "NEW")

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_when_get_list_fails(self, mock_request):
        with suppress(AttributeError):
            del app.surveys_dict
        mock_request.get(url_get_survey_list, status_code=500)
        self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), None)

    @requests_mock.mock()
    def test_get_survey_short_name_by_id_when_id_not_found(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)
        self.assertEqual(get_survey_short_name_by_id("not_a_valid_survey_id"), None)

        # Check cached dictionary is preserved
        mock_request.get(url_get_survey_list, status_code=500)
        self.assertEqual(get_survey_short_name_by_id("cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"), "BRES")
