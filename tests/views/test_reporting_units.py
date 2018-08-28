import json

import requests_mock

from config import TestingConfig
from tests.views import ViewTestCase


respondent_party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
business_party_id = 'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c'
ru_ref = '50012345678'
collection_exercise_id_1 = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
collection_exercise_id_2 = '9af403f8-5fc5-43b1-9fca-afbd9c65da5c'
iac_1 = 'jkbvyklkwj88'
iac_2 = 'ljbgg3kgstr4'
survey_id = 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87'
case_id = '10b04906-f478-47f9-a985-783400dd8482'
CONNECTION_ERROR = 'Connection error'

url_search_reporting_units = f'{TestingConfig.PARTY_URL}/party-api/v1/businesses/search'
get_respondent_by_id_url = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{respondent_party_id}'
url_edit_contact_details = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{respondent_party_id}'
url_post_case_event = f'{TestingConfig.CASE_URL}/cases/{case_id}/events'
url_change_enrolment_status = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/change_enrolment_status'
url_resend_verification_email = f'{TestingConfig.PARTY_URL}/party-api/v1/resend-verification-email' \
                                f'/{respondent_party_id}'

url_get_party_by_ru_ref = f'{TestingConfig.PARTY_URL}/party-api/v1/parties/type/B/ref/{ru_ref}'
url_get_cases_by_business_party_id = f'{TestingConfig.CASE_URL}/cases/partyid/{business_party_id}'
url_get_casegroups_by_business_party_id = f'{TestingConfig.CASE_URL}/casegroups/partyid/{business_party_id}'
url_get_collection_exercise_by_id = f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
url_get_business_party_by_party_id = f'{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}'
url_get_available_case_group_statuses_direct = f'{TestingConfig.CASE_URL}/casegroups/transitions' \
                                               f'/{collection_exercise_id_1}/{ru_ref}'
url_get_survey_by_id = f'{TestingConfig.SURVEY_URL}/surveys/{survey_id}'
url_get_respondent_party_by_party_id = f'{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{respondent_party_id}'
url_get_iac = f'{TestingConfig.IAC_URL}/iacs'
url_get_case = f'{TestingConfig.CASE_URL}/cases/{case_id}?iac=true'

with open('tests/test_data/reporting_units/respondent.json') as fp:
    respondent = json.load(fp)
with open('tests/test_data/reporting_units/respondent_with_pending_email.json') as fp:
    respondent_with_pending_email = json.load(fp)
with open('tests/test_data/case/case.json') as fp:
    case = json.load(fp)

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


class TestReportingUnits(ViewTestCase):

    def setup_data(self):
        self.case_group_status = {
            "ru_ref": "19000001",
            "ru_name": "RU Name",
            "trading_as": "Company Name",
            "survey_id": "123",
            "short_name": "MYSURVEY",
            "current_status": "NOTSTARTED",
            "available_statuses": {
                "UPLOADED": "COMPLETE",
                "COMPLETED_BY_PHONE": "COMPLETEDBYPHONE"
            }
        }

    @requests_mock.mock()
    def test_get_reporting_unit(self, mock_request):
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

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)
        self.assertIn("BLOCKS".encode(), response.data)
        self.assertIn("GB".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)
        self.assertIn("Enabled".encode(), response.data)
        self.assertIn("Active".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_party_ru_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_cases_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_cases_404(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, status_code=404)
        mock_request.get(url_get_casegroups_by_business_party_id, json=[])
        mock_request.get(url_get_respondent_party_by_party_id, json=[])

        response = self.client.get("/reporting-units/50012345678")

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_reporting_unit_casegroups_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_casegroups_404(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=[])
        mock_request.get(url_get_casegroups_by_business_party_id, status_code=404)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_collection_exercise_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', status_code=500)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 4)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_party_id_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 6)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_casegroup_status_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 7)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_casegroup_status_404(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, status_code=404)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', json=iac)
        mock_request.get(f'{url_get_iac}/{iac_2}', json=iac)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_reporting_unit_survey_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        # TODO: url_get_business_party_by_party_id and url_get_available_case_group_statuses_direct are called twice
        # duplicated calls should probably be refactored out
        self.assertEqual(len(request_history), 10)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_respondent_party_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        # TODO: url_get_business_party_by_party_id and url_get_available_case_group_statuses_direct are called twice
        # duplicated calls should probably be refactored out
        self.assertEqual(len(request_history), 11)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_iac_fail(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        # TODO: url_get_business_party_by_party_id and url_get_available_case_group_statuses_direct are called twice
        # duplicated calls should probably be refactored out
        self.assertEqual(len(request_history), 12)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_iac_404(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', status_code=404)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_when_changed_status_shows_new_status(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups_completed)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', json=iac)
        mock_request.get(f'{url_get_iac}/{iac_2}', json=iac)

        response = self.client.get("/reporting-units/50012345678?survey=BLOCKS&period=201801", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Response status for 221 BLOCKS period 201801 changed to Completed".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_shows_change_link(self, mock_request):
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

        response = self.client.get("/reporting-units/50012345678")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Change</a>".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_hides_change_link_when_no_available_statuses(self, mock_request):
        mock_request.get(url_get_party_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_1}', json=collection_exercise)
        mock_request.get(f'{url_get_collection_exercise_by_id}/{collection_exercise_id_2}', json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json={})
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f'{url_get_iac}/{iac_1}', json=iac)
        mock_request.get(f'{url_get_iac}/{iac_2}', json=iac)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Change</a>".encode(), response.data)

    @requests_mock.mock()
    def test_search_reporting_units(self, mock_request):
        businesses = [{'name': 'test', 'ruref': '123456'}]
        mock_request.get(url_search_reporting_units, json=businesses)

        response = self.client.post("/reporting-units")

        self.assertEqual(response.status_code, 200)
        self.assertIn("test".encode(), response.data)
        self.assertIn("123456".encode(), response.data)

    @requests_mock.mock()
    def test_search_reporting_units_fail(self, mock_request):
        mock_request.get(url_search_reporting_units, status_code=500)

        response = self.client.post("/reporting-units", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_resend_verification_email(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent)
        response = self.client.get(
            f"reporting-units/resend_verification/50012345678/{respondent_party_id}")
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_resend_verification_email_to_pending_email_address(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent_with_pending_email)
        response = self.client.get(
            f"reporting-units/resend_verification/50012345678/{respondent_party_id}")
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_resent_verification_email(self, mock_request):
        mock_request.get(url_resend_verification_email)
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

        response = self.client.post(
            f"reporting-units/resend_verification/50012345678/{respondent_party_id}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_fail_resent_verification_email(self, mock_request):
        mock_request.get(url_resend_verification_email, status_code=500)
        response = self.client.post(f"reporting-units/resend_verification/50012345678/{respondent_party_id}",
                                    follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_contact_details(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent)

        response = self.client.get(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Jacky".encode(), response.data)
        self.assertIn("Turner".encode(), response.data)
        self.assertIn("0987654321".encode(), response.data)

    @requests_mock.mock()
    def test_get_contact_details_fail(self, mock_request):
        mock_request.get(get_respondent_by_id_url, status_code=500)

        response = self.client.get(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                   follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_edit_contact_details(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161867'}
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_edit_contact_details_email_already_exists(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161859'}
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details, status_code=409)

        response = self.client.post(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                    data=changed_details, follow_redirects=True)

        self.assertIn('Error - email address already exists'.encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_404_response(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161859'}
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details, status_code=404)

        response = self.client.post(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                    data=changed_details, follow_redirects=True)

        self.assertIn(CONNECTION_ERROR.encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_500_response(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161867'}
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details, status_code=500)

        response = self.client.post(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                    data=changed_details, follow_redirects=True)

        self.assertIn(CONNECTION_ERROR.encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_error_response(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161867'}
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details, status_code=405)

        response = self.client.post(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                    data=changed_details, follow_redirects=True)

        self.assertIn(CONNECTION_ERROR.encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_last_name_change(self, mock_request):
        changed_details = {
            "first_name": 'Jacky',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161859'}
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

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
        response = self.client.post(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                    data=changed_details, follow_redirects=True)
        return response

    @requests_mock.mock()
    def test_edit_contact_details_telephone_change(self, mock_request):
        changed_details = {
            "first_name": 'Jacky',
            "last_name": 'Turner',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161867'}
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_edit_contact_details_email_change(self, mock_request):
        changed_details = {
            "first_name": 'Jacky',
            "last_name": 'Turner',
            "email": 'Jacky.Turner@thisemail.com',
            "telephone": '7971161859'}
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

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
    def test_reporting_unit_generate_new_code(self, mock_request):
        mock_request.post(url_post_case_event)
        mock_request.get(url_get_case, json=case)

        response = self.client.get(f"/reporting-units/{ru_ref}/new_enrolment_code?case_id={case['id']}&"
                                   "survey_name=test_survey_name&trading_as=trading_name&ru_name=test_ru_name",
                                   follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("jkbvyklkwj88".encode(), response.data)
        self.assertIn("test_ru_name".encode(), response.data)
        self.assertIn("trading_name".encode(), response.data)
        self.assertIn("test_survey_name".encode(), response.data)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code_event_fail(self, mock_request):
        mock_request.post(url_post_case_event, status_code=500)

        response = self.client.get(f"/reporting-units/{ru_ref}/new_enrolment_code?case_id={case['id']}",
                                   follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code_case_fail(self, mock_request):
        mock_request.post(url_post_case_event)
        mock_request.get(url_get_case, status_code=500)

        response = self.client.get(f"/reporting-units/{ru_ref}/new_enrolment_code?case_id={case['id']}&"
                                   "survey_name=test_survey_name&trading_as=trading_name&ru_name=test_ru_name",
                                   follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    def test_disable_enrolment_view(self):
        response = self.client.get("/reporting-units/ru_ref/change-enrolment-status"
                                   "?survey_id=test_id&survey_name=test_survey_name&respondent_id=test_id"
                                   "&respondent_first_name=first_name&respondent_last_name=last_name"
                                   "&business_id=test_id"
                                   "&trading_as=test_name&change_flag=DISABLED&ru_name=test_ru_name")

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_ru_name".encode(), response.data)
        self.assertIn("test_name".encode(), response.data)
        self.assertIn("test_survey_name".encode(), response.data)
        self.assertIn("first_name".encode(), response.data)
        self.assertIn("Disable enrolment".encode(), response.data)

    @requests_mock.mock()
    def test_disable_enrolment_post(self, mock_request):
        mock_request.put(url_change_enrolment_status)
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

        response = self.client.post("/reporting-units/50012345678/change-enrolment-status"
                                    "?survey_id=test_id&respondent_id=test_id&business_id=test_id&change_flag=DISABLED",
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)

    @requests_mock.mock()
    def test_disable_enrolment_post_fail(self, mock_request):
        mock_request.put(url_change_enrolment_status, status_code=500)

        response = self.client.post("/reporting-units/50012345678/change-enrolment-status"
                                    "?survey_id=test_id&respondent_id=test_id&business_id=test_id&change_flag=DISABLED",
                                    follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)
