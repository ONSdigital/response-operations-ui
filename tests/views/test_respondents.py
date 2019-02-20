import json

import requests_mock

from config import TestingConfig
from response_operations_ui.controllers.party_controller import search_respondent_by_email
from tests.views import ViewTestCase
from tests.views.test_reporting_units import url_edit_contact_details, url_get_party_by_ru_ref, \
    url_get_casegroups_by_business_party_id, url_get_cases_by_business_party_id, url_get_business_party_by_party_id, \
    url_get_available_case_group_statuses_direct, url_get_survey_by_id, url_get_respondent_party_by_party_id, \
    url_get_collection_exercise_by_id, url_get_iac, url_change_respondent_status

respondent_party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
collection_exercise_id_1 = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
collection_exercise_id_2 = '9af403f8-5fc5-43b1-9fca-afbd9c65da5c'
get_business_by_id_url = f'{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}'
get_respondent_by_email_url = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/email'
get_respondent_by_id_url = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{party_id}'
get_survey_by_id_url = f'{TestingConfig.SURVEY_URL}/surveys/{survey_id}'
iac_1 = 'jkbvyklkwj88'
iac_2 = 'ljbgg3kgstr4'

with open('tests/test_data/reporting_units/respondent.json') as json_data:
    respondent = json.load(json_data)
with open('tests/test_data/reporting_units/reporting_unit.json') as json_data:
    reporting_unit = json.load(json_data)
with open('tests/test_data/survey/survey_by_id.json') as json_data:
    survey_by_id = json.load(json_data)
with open('tests/test_data/party/business_reporting_unit.json') as fp:
    business_reporting_unit = json.load(fp)
with open('tests/test_data/case/cases_list.json') as fp:
    cases_list = json.load(fp)
with open('tests/test_data/case/case_groups_list.json') as fp:
    case_groups = json.load(fp)
with open('tests/test_data/case/case_groups_list_completed.json') as fp:
    case_groups_completed = json.load(fp)
with open('tests/test_data/collection_exercise/collection_exercise.json') as fp:
    collection_exercise = json.load(fp)
with open('tests/test_data/party/business_party.json') as fp:
    business_party = json.load(fp)
with open('tests/test_data/case/case_group_statuses.json') as fp:
    case_group_statuses = json.load(fp)
with open('tests/test_data/survey/single_survey.json') as fp:
    survey = json.load(fp)
with open('tests/test_data/party/respondent_party.json') as fp:
    respondent_party = json.load(fp)
with open('tests/test_data/iac/iac.json') as fp:
    iac = json.load(fp)


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

    def mock_for_change_details(self, changed_details, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details)
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', json=iac)
        mock_request.get(f'{url_get_iac}/{iac_2}', json=iac)
        response = self.client.post(f"/respondents/edit-contact-details/{respondent_party_id}",
                                    data=changed_details, follow_redirects=True)
        return response

    @requests_mock.mock()
    def test_edit_contact_details_and_email_change(self, mock_request):
        changed_details = {
            "first_name": 'Jacky',
            "last_name": 'Turner',
            "email": 'Jacky.Turner@thisemail.com',
            "telephone": '7971161867'}
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_change_respondent_status(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', json=iac)
        mock_request.get(f'{url_get_iac}/{iac_2}', json=iac)

        response = self.client.post(f"respondents/{respondent_party_id}/change-respondent-status"
                                    f"?tab=respondents&change_flag=ACTIVE",
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
