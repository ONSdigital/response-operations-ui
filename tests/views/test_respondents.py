import json

import requests_mock

from config import TestingConfig
from response_operations_ui.controllers.party_controller import search_respondent_by_email
from tests.views import ViewTestCase


business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
get_business_by_id_url = f'{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}'
get_respondent_by_email_url = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/email'
get_respondent_by_id_url = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{party_id}'
get_survey_by_id_url = f'{TestingConfig.SURVEY_URL}/surveys/{survey_id}'

with open('tests/test_data/reporting_units/respondent.json') as json_data:
    respondent = json.load(json_data)
with open('tests/test_data/reporting_units/reporting_unit.json') as json_data:
    reporting_unit = json.load(json_data)
with open('tests/test_data/survey/survey_by_id.json') as json_data:
    survey_by_id = json.load(json_data)


class TestRespondents(ViewTestCase):

    def setup_data(self):
        pass

    def test_search_respondent_get(self):
        response = self.client.get("/respondents")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Respondents".encode(), response.data)

    @requests_mock.mock()
    def test_get_respondent_by_email_success(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json=respondent, status_code=200)

        with self.app.app_context():
            response = search_respondent_by_email(email)

        self.assertEqual(response['firstName'], 'Jacky')

    @requests_mock.mock()
    def test_get_respondent_by_email_no_respondent(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json={"Response": "No respondent found"}, status_code=404)

        with self.app.app_context():
            response = search_respondent_by_email(email)

        assert response is None

    @requests_mock.mock()
    def test_search_respondent_by_email_server_error(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, status_code=500)

        response = self.client.post("/respondents/", data={"email": email})

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_search_respondent_by_email_success(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_respondent_by_email_url, json=respondent, status_code=200)
        mock_request.get(get_respondent_by_id_url, json=respondent, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey_by_id, status_code=200)

        response = self.client.post("/respondents", data={"query": email}, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_search_respondent_by_email_no_respondent(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, status_code=404)

        response = self.client.post("/respondents/", data={"query": email}, follow_redirects=True)

        self.assertIn('No Respondent found'.encode(), response.data)

    @requests_mock.mock()
    def test_search_respondent_by_email_unable_to_get_survey(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=200)
        mock_request.get(get_respondent_by_email_url, json=respondent, status_code=200)
        mock_request.get(get_respondent_by_id_url, json=respondent, status_code=200)
        mock_request.get(get_survey_by_id_url, json=survey_by_id, status_code=500)

        response = self.client.post("/respondents", data={"query": email}, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 4)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_search_respondent_by_email_unable_to_get_respondent_details(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json=respondent, status_code=200)
        mock_request.get(get_respondent_by_id_url, json=respondent, status_code=500)

        response = self.client.post("/respondents", data={"query": email}, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_search_respondent_by_email_unable_to_get_business_details(self, mock_request):
        email = 'Jacky.Turner@email.com'
        mock_request.get(get_respondent_by_email_url, json=respondent, status_code=200)
        mock_request.get(get_respondent_by_id_url, json=respondent, status_code=200)
        mock_request.get(get_business_by_id_url, json=reporting_unit, status_code=500)

        response = self.client.post("/respondents", data={"query": email}, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)
