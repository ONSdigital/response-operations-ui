import json
import unittest
from unittest.mock import MagicMock

from requests import RequestException
import requests_mock

from response_operations_ui import app


url_get_survey_list = '{}/{}'.format(app.config['BACKSTAGE_API_URL'], 'survey/surveys')
with open('tests/test_data/survey/survey_list.json') as json_data:
    survey_list = json.load(json_data)


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
