import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app

short_name = 'BLOCKS'
survey_id = 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87'
period = '201801'
collection_exercise_id = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
ru_ref = '19000001'
business_party_id = 'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c'

url_get_survey_by_short_name = f'{app.config["SURVEY_URL"]}/surveys/shortname/{short_name}'
url_get_collection_exercises_by_survey = f'{app.config["COLLECTION_EXERCISE_URL"]}' \
                                         f'/collectionexercises/survey/{survey_id}'
url_get_party_by_ru_ref = f'{app.config["PARTY_URL"]}/party-api/v1/parties/type/B/ref/{ru_ref}'
url_get_available_case_group_statuses = f'{app.config["CASE_URL"]}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'
url_get_case_groups_by_business_party_id = f'{app.config["CASE_URL"]}/casegroups/partyid/{business_party_id}'
url_update_case_group_status = f'{app.config["CASE_URL"]}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'

with open('tests/test_data/survey/single_survey.json') as fp:
    survey = json.load(fp)
with open('tests/test_data/collection_exercise/collection_exercise_list.json') as fp:
    collection_exercise_list = json.load(fp)
with open('tests/test_data/party/business_reporting_unit.json') as fp:
    business_reporting_unit = json.load(fp)
with open('tests/test_data/case/case_groups_list.json') as fp:
    case_groups = json.load(fp)


class TestChangeResponseStatus(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()
        self.statuses = {
            'COLLECTION_INSTRUMENT_DOWNLOADED': 'INPROGRESS',
            'EQ_LAUNCH': 'INPROGRESS',
            'SUCCESSFUL_RESPONSE_UPLOAD': 'COMPLETE',
            'COMPLETED_BY_PHONE': 'COMPLETEDBYPHONE'
        }

    @requests_mock.mock()
    def test_get_available_status(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups)

        response = self.app.get(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}')

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'19000001', data)
        self.assertIn(b'Bolts and Ratchets', data)
        self.assertIn(b'221 &nbsp; BLOCKS', data)
        self.assertIn(b'Not started', data)
        self.assertIn(b'Completed by phone', data)

    @requests_mock.mock()
    def test_get_available_status_survey_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.app.get(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_available_status_collection_exercise_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, status_code=500)

        response = self.app.get(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_available_status_party_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_party_by_ru_ref, status_code=500)

        response = self.app.get(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_available_status_case_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, status_code=500)

        response = self.app.get(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_available_status_case_group_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, status_code=500)

        response = self.app.get(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_update_case_group_status(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.put(url_update_case_group_status)

        response = self.app.post(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                 data={'event': 'COMPLETEDBYPHONE'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('reporting-unit', response.location)

    @requests_mock.mock()
    def test_update_case_group_status(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.put(url_update_case_group_status)

        response = self.app.post(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                 data={'event': 'COMPLETEDBYPHONE'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('reporting-unit', response.location)

    @requests_mock.mock()
    def test_update_case_group_status_no_event(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.put(url_update_case_group_status)

        response = self.app.post(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}')

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('reporting-unit', response.location)

    @requests_mock.mock()
    def test_update_case_group_status_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.put(url_update_case_group_status, status_code=500)

        response = self.app.post(f'/case/{ru_ref}/change-response-status?survey={short_name}&period={period}',
                                 data={'event': 'COMPLETEDBYPHONE'}, follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)