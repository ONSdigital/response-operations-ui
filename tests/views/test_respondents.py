import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.party_controller import search_respondent_by_email

party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
backstage_api_url = app.config["BACKSTAGE_API_URL"]
url_get_reporting_unit = f'{backstage_api_url}/v1/reporting-unit/50012345678'
get_respondent_by_email_url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/email'
get_respondent_by_id_url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/id/{party_id}'
put_respondent_account_status_by_id_url = f'{app.config["PARTY_SERVICE_URL"]}/party-api/v1/respondents/edit-account-status/{party_id}'

with open('tests/test_data/reporting_units/respondent.json') as json_data:
    respondent = json.load(json_data)
with open('tests/test_data/reporting_units/reporting_unit.json') as json_data:
    reporting_unit = json.load(json_data)


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
            f'respondents/change-respondent-account-status?party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEquals(response.status_code, 200)

    @requests_mock.mock()
    def test_suspend_respondent_account_server_error(self, mock_request):
        mock_request.put(put_respondent_account_status_by_id_url, json={"status_change": "SUSPENDED"}, status_code=500)

        response = self.app.post(
            f'respondents/change-respondent-account-status?party_id={respondent["respondent_party"]["id"]}&ru_ref=50012345678&change_status=SUSPENDED',
            follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)