from copy import deepcopy
import unittest
import os
import json

import requests_mock

from response_operations_ui import create_app
from response_operations_ui.views.home import get_sample_data

project_root = os.path.dirname(os.path.dirname(__file__))

url_dashboard = ("http://localhost:8084/reporting-api/v1/response-dashboard/survey/75b19ea0-69a4-4c58-8d7f-4458c8f43f5c"
                 "/collection-exercise/aec41b04-a177-4994-b385-a16136242d05")

reporting_json = {
    'metadata': {
        'timeUpdated': 1592493454.328932,
        'collectionExerciseId': "aec41b04-a177-4994-b385-a16136242d05"
    },
    'report': {
        'inProgress': 600,
        'accountsPending': 200,
        'accountsEnrolled': 800,
        'notStarted': 100,
        'completed': 700,
        'sampleSize': 1000
    }
}

surveys_json = {"id": "75b19ea0-69a4-4c58-8d7f-4458c8f43f5c",
                "legalBasis": "Statistics of Trade Act 1947",
                "longName": "Monthly Business Survey - Retail Sales Index",
                "shortName": "RSI",
                "surveyRef": "023"}


class TestSignIn(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')

    @requests_mock.mock()
    def test_get_sample_data(self, mock_request):
        """Tests getting sample data when everything is working as expected"""
        mock_request.get(url_dashboard, json=reporting_json, status_code=200)
        
        with open(f"{project_root}/test_data/collection_exercise/closest_past_collection_exercise.json") as json_data:
            collection_exercise = json.load(json_data)

        expected_url = 'http://localhost:8078/dashboard/collection-exercise/aec41b04-a177-4994-b385-a16136242d05'
        expected_output = {'completed': '700 (70.0%)',
                           'dashboard_url': expected_url,
                           'in_progress': '600',
                           'not_started': '100',
                           'sample_size': '1000'}
        with self.app.app_context():
            output = get_sample_data(collection_exercise, surveys_json)
            self.assertEqual(output, expected_output)

    @requests_mock.mock()
    def test_get_sample_data_collection_exercise_or_survey_not_found(self, mock_request):
        """If the survey or collection exercise are invalid, a 404 will be returned and the sample data section
        will return mostly 'N/A'.  The dashboard url will still present with the info available."""
        mock_request.get(url_dashboard, json={'message': 'Invalid collection exercise or survey ID'}, status_code=404)

        with open(f"{project_root}/test_data/collection_exercise/closest_past_collection_exercise.json") as json_data:
            collection_exercise = json.load(json_data)

        expected_url = 'http://localhost:8078/dashboard/collection-exercise/aec41b04-a177-4994-b385-a16136242d05'
        expected_output = {'completed': 'N/A',
                           'dashboard_url': expected_url,
                           'in_progress': 'N/A',
                           'not_started': 'N/A',
                           'sample_size': 'N/A'}
        with self.app.app_context():
            output = get_sample_data(collection_exercise, surveys_json)
            self.assertEqual(output, expected_output)

    @requests_mock.mock()
    def test_get_sample_data_zero_sample_size(self, mock_request):
        """Tests getting sample data and the sample size is 0.  This should display the hardcoded 0 for completed.
        We hardcode it because if we tried to divide by 0 then we'd get an exception."""
        copied_dashboard_response = deepcopy(reporting_json)
        copied_dashboard_response['report']['sampleSize'] = 0
        mock_request.get(url_dashboard, json=copied_dashboard_response, status_code=200)

        with open(f"{project_root}/test_data/collection_exercise/closest_past_collection_exercise.json") as json_data:
            collection_exercise = json.load(json_data)

        expected_url = 'http://localhost:8078/dashboard/collection-exercise/aec41b04-a177-4994-b385-a16136242d05'
        expected_output = {'completed': '0 (0.0%)',
                           'dashboard_url': expected_url,
                           'in_progress': '600',
                           'not_started': '100',
                           'sample_size': '0'}
        with self.app.app_context():
            output = get_sample_data(collection_exercise, surveys_json)
            self.assertEqual(output, expected_output)
