import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.party_controller import get_respondent_enrolments, search_respondent_by_email

business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
backstage_api_url = app.config["BACKSTAGE_API_URL"]
url_get_reporting_unit = f'{backstage_api_url}/v1/reporting-unit/50012345678'
get_respondent_by_email_url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/email'
get_respondent_by_id_url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/id/{party_id}'
put_respondent_account_status_by_id_url = \
    f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/edit-account-status/{party_id}'
get_business_by_id_url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/businesses/id/{business_party_id}'
get_survey_by_id_url = f'{app.config["SURVEY_SERVICE_URL"]}/surveys/{survey_id}'

with open('tests/test_data/respondent/respondent.json') as json_data:
    respondent = json.load(json_data)
with open('tests/test_data/respondent/respondent_disabled_enrolment.json') as json_data:
    respondent_no_enabled_enrolment = json.load(json_data)
with open('tests/test_data/reporting_units/reporting_unit.json') as json_data:
    reporting_unit = json.load(json_data)
with open('tests/test_data/survey/survey.json') as json_data:
    survey = json.load(json_data)


class TestRespondents(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()
        self.case_group_status = {
            "ru_ref": "19000001",
            "trading_as": "Company Name",
            "survey_id": "123",
            "short_name": "MYSURVEY",
            "current_status": "NOTSTARTED",
            "available_statuses": {
                "UPLOADED": "COMPLETE",
                "COMPLETED_BY_PHONE": "COMPLETEDBYPHONE"
            }
        }

    def test_search_respondent_get(self):
        response = self.app.get("/respondents")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Respondents".encode(), response.data)

    @requests_mock.mock()
    def test_get_respondent_by_email_success(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json=respondent['respondent_party'], status_code=200)

        response = search_respondent_by_email(email)

        self.assertEquals(response['firstName'], 'Jacky')

    @requests_mock.mock()
    def test_get_respondent_by_email_no_respondent(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json={"Response": "No respondent found"}, status_code=404)

        response = search_respondent_by_email(email)

        self.assertEquals(response['Response'], 'No respondent found')

    @requests_mock.mock()
    def test_search_respondent_by_email_server_error(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, status_code=500)

        response = self.app.post("/respondents/", data={"email": email}, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_search_respondent_by_email_success(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json=respondent['respondent_party'], status_code=200)
        mock_request.get(get_respondent_by_id_url, json=respondent, status_code=200)

        response = self.app.post("/respondents", data={"query": email}, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_search_respondent_by_email_no_respondent(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json={"Response": "No respondent found"}, status_code=200)

        response = self.app.post("/respondents/", data={"query": email}, follow_redirects=True)

        self.assertIn('No Respondent found.'.encode(), response.data)

    @requests_mock.mock()
    def test_suspend_respondent_account_status_success(self, mock_request):
        mock_request.put(put_respondent_account_status_by_id_url, json={"status_change": "SUSPENDED"}, status_code=200)
        mock_request.get(url_get_reporting_unit, json=reporting_unit)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201802/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201802/50012345678',
                         json=self.case_group_status)

        response = self.app.post(
            f'respondents/change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEquals(response.status_code, 200)

    @requests_mock.mock()
    def test_suspend_respondent_account_server_error(self, mock_request):
        mock_request.put(put_respondent_account_status_by_id_url, json={"status_change": "SUSPENDED"}, status_code=500)

        response = self.app.post(
            f'respondents/change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_confirm_account_status_change_success(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent, status_code=200)
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey, status_code=200)

        response = self.app.get(
            f'/respondents/confirm-change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Suspend account?".encode(), response.data)

    @requests_mock.mock()
    def test_confirm_account_status_change_no_enabled_enrolments(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent_no_enabled_enrolment, status_code=200)
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey, status_code=200)

        response = self.app.get(
            f'/respondents/confirm-change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED')

        self.assertEqual(response.status_code, 200)
        self.assertIn("No enrolments currently enabled".encode(), response.data)

    @requests_mock.mock()
    def test_confirm_account_status_error_retrieveing_business(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent_no_enabled_enrolment, status_code=200)
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=500)
        mock_request.get(get_survey_by_id_url, json=survey, status_code=200)

        response = self.app.get(
            f'/respondents/confirm-change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_confirm_account_status_error_retrieveing_respondent(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent_no_enabled_enrolment, status_code=500)
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey, status_code=200)

        response = self.app.get(
            f'/respondents/confirm-change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_confirm_account_status_error_retrieveing_survey(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent_no_enabled_enrolment, status_code=200)
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey, status_code=500)

        response = self.app.get(
            f'/respondents/confirm-change-respondent-account-status?'
            f'party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_get_all_respondent_enrolments(self, mock_request):
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey, status_code=200)

        enrolments = get_respondent_enrolments(respondent['respondent_party'])

        self.assertEqual(enrolments[0]['business']['reporting_unit']['id'], business_party_id)
        self.assertEqual(enrolments[0]['survey']['survey']['id'], survey_id)
