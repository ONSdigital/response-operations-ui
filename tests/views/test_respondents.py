import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.respondent_controllers import search_respondent_by_email

party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
get_respondent_by_email_url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/get-respondent-by-email'
get_respondent_by_id_url = f'{app.config["BACKSTAGE_API_URL"]}/v1/party/party-details?respondent_party_id={party_id}'

with open('tests/test_data/reporting_units/respondent.json') as json_data:
    respondent = json.load(json_data)


class TestRespondents(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

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
