import json
import unittest
from unittest.mock import MagicMock

from requests import RequestException
import requests_mock

from response_operations_ui import app


url_get_survey_list = f'{app.config["BACKSTAGE_API_URL"]}/survey/surveys'
with open('tests/test_data/survey/survey_list.json') as json_data:
    survey_list = json.load(json_data)
url_get_survey_by_short_name = f'{app.config["BACKSTAGE_API_URL"]}/survey/shortname/bres'
with open('tests/test_data/survey/survey.json') as json_data:
    survey_info = json.load(json_data)
url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/collection-exercise/test/000000'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)


class TestSurvey(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @requests_mock.mock()
    def test_survey_list(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_fail(self, mock_request):
        mock_request.get(url_get_survey_list, status_code=500)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_connection_error(self, mock_request):
        mock_request.get(url_get_survey_list, exc=RequestException(request=MagicMock()))

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_survey_view(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey_info)

        response = self.app.get("/surveys/bres")

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_view_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.app.get("/surveys/bres")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("000000".encode(), response.data)
        self.assertIn("January 2017".encode(), response.data)
        self.assertIn("15 May 1993".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_no_reminder(self, mock_request):
        del collection_exercise_details['events']['firstReminder']
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("000000".encode(), response.data)
        self.assertIn("January 2017".encode(), response.data)
        self.assertIn("15 May 1993".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_fail(self, mock_request):
        mock_request.get(url_get_collection_exercise, status_code=500)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)
