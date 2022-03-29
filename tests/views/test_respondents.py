import json
import os

import jwt
import mock
import requests_mock
from bs4 import BeautifulSoup

from config import TestingConfig
from response_operations_ui import create_app
from tests.views import ViewTestCase
from tests.views.test_admin import url_permission_url, url_sign_in_data
from tests.views.test_reporting_units import (
    url_change_respondent_status,
    url_edit_contact_details,
    url_get_business_by_ru_ref,
    url_get_cases_by_business_party_id,
    url_get_collection_exercise_by_id,
    url_get_iac,
    url_get_respondent_party_by_party_id,
    url_get_survey_by_id,
)
from tests.views.test_sign_in import url_surveys

respondent_party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
collection_exercise_id_1 = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
collection_exercise_id_2 = "9af403f8-5fc5-43b1-9fca-afbd9c65da5c"
ru_ref = "50012345678"

get_business_by_id_url = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}"
get_respondent_by_email_url = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/email"
get_respondent_by_id_url = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{party_id}"
get_survey_by_id_url = f"{TestingConfig.SURVEY_URL}/surveys/{survey_id}"
url_auth_respondent_account = f"{TestingConfig.AUTH_URL}/api/account/user"
url_get_business_party_by_party_id = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}"
url_get_casegroups_by_business_party_id = f"{TestingConfig.CASE_URL}/casegroups/partyid/{business_party_id}"
url_get_available_case_group_statuses_direct = (
    f"{TestingConfig.CASE_URL}/casegroups/transitions" f"/{collection_exercise_id_1}/{ru_ref}"
)
url_get_pending_share = f"{TestingConfig.PARTY_URL}/party-api/v1/pending-surveys/originator/" f"{respondent_party_id}"
url_post_resend_pending_share_email = f"{TestingConfig.PARTY_URL}/party-api/v1/pending-surveys/resend-email"
batch_number = "21983359-d944-4707-8979-299a433daed8"
url_post_delete_pending_share = f"{TestingConfig.PARTY_URL}/party-api/v1/pending-surveys/{batch_number}"
iac_1 = "jkbvyklkwj88"
iac_2 = "ljbgg3kgstr4"

get_respondent_root = "http://localhost:8085/party-api/v1/respondents/"
get_respondent_root_with_trailing_slash = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/"
url_resend_verification_email = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/resend-account-email-change-notification" f"/{respondent_party_id}"
)

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/reporting_units/respondent.json") as json_data:
    respondent = json.load(json_data)
with open(f"{project_root}/test_data/reporting_units/reporting_unit.json") as json_data:
    reporting_unit = json.load(json_data)
with open(f"{project_root}/test_data/survey/survey_by_id.json") as json_data:
    survey_by_id = json.load(json_data)
with open(f"{project_root}/test_data/party/business_reporting_unit.json") as fp:
    business_reporting_unit = json.load(fp)
with open(f"{project_root}/test_data/case/cases_list.json") as fp:
    cases_list = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list.json") as fp:
    case_groups = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list_completed.json") as fp:
    case_groups_completed = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as fp:
    collection_exercise = json.load(fp)
with open(f"{project_root}/test_data/party/business_party.json") as fp:
    business_party = json.load(fp)
with open(f"{project_root}/test_data/case/case_group_statuses.json") as fp:
    case_group_statuses = json.load(fp)
with open(f"{project_root}/test_data/survey/single_survey.json") as fp:
    survey = json.load(fp)
with open(f"{project_root}/test_data/party/respondent_party.json") as fp:
    respondent_party = json.load(fp)
with open(f"{project_root}/test_data/iac/iac.json") as fp:
    iac = json.load(fp)
with open(f"{project_root}/test_data/pending_survey/share.json") as fp:
    share = json.load(fp)
with open(f"{project_root}/test_data/pending_survey/transfer.json") as fp:
    transfer = json.load(fp)

user_permission_respondent_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "respondents.edit", "type": "DIRECT"}],
}

user_permission_respondent_delete_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "respondents.delete", "type": "DIRECT"}],
}


class TestRespondents(ViewTestCase):
    def setup_data(self):
        self.app = create_app("TestingConfig")
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.surveys_list_json = [
            {
                "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
                "shortName": "ASHE",
                "longName": "ASHE long name",
                "surveyRef": "123",
            }
        ]

    def mock_for_change_details(self, changed_details, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        response = self.client.post(
            f"/respondents/edit-contact-details/{respondent_party_id}", data=changed_details, follow_redirects=True
        )
        return response

    @requests_mock.mock()
    def test_edit_contact_details_and_email_change(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_pending_share, json=[])
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Turner",
            "email": "Jacky.Turner@thisemail.com",
            "telephone": "7971161867",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_edit_contact_details_email_change_with_trailing_space(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_pending_share, json=[])
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Turner",
            "email": r"Jacky.Turner@thisemail.com ",
            "telephone": "7971161867",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNot(r"Jacky.Turner@thisemail.com ".encode(), response.data)

    @requests_mock.mock()
    def test_change_respondent_status(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.put(url_change_respondent_status)
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=[])

        response = self.client.post(
            f"respondents/{respondent_party_id}/change-respondent-status" f"?tab=respondents&change_flag=ACTIVE",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    # Respondent Search UI Testing
    @staticmethod
    def _mock_party_data(search_respondents_mock, total=1000):
        with open(f"{project_root}/test_data/party/mock_search_respondents_data.json", "r") as json_file:
            data = json.load(json_file)
            search_respondents_mock.return_value = {"data": data, "total": total}

    # Landing Page
    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_root_view_renders_form_without_trailing_slash(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock)

        response = self.client.get("/respondents")
        self.assertEqual(response.status_code, 200, "Loading respondent landing page failed")

        soup = BeautifulSoup(response.data, features="html.parser")
        page_titles = [h1.text for h1 in soup.findAll("h1")]

        self.assertTrue("Find a respondent" in page_titles, "Could not find respondent landing page title")

    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_root_view_renders_form_with_trailing_slash(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock)

        response = self.client.get("/respondents/")
        self.assertEqual(response.status_code, 200, "Loading respondent landing page failed")

        soup = BeautifulSoup(response.data, features="html.parser")
        elements = [el.text for el in soup.findAll("h1")]

        self.assertTrue("Find a respondent" in elements, "Could not find respondent landing page title")

    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_posting_invalid_form_shows_landing_page_with_error(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock)

        response = self.client.post("/respondents/search", data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Sending search form failed")

        soup = BeautifulSoup(response.data, features="html.parser")
        elements_text = [el.text for el in soup.findAll("a")]

        self.assertTrue("At least one input should be filled" in elements_text, "Could not find expected error message")

    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_posting_form_with_valid_input_goes_to_results_page(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock)

        response = self.client.post("/respondents/search", data={"first_name": "a"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Sending search form failed")

        self.assertTrue(b"respondents found" in response.data, "Could not find expected error message")

    # Results page
    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_results_page_shows_correct_number_of_results(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock, 1)
        response = self.client.post("/respondents/search", data={"first_name": "sophey"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Sending search form failed")

        self.assertTrue(b"1 respondents found." in response.data, "Could not find required page element")

    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_results_page_shows_pagination_if_needed(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock)
        response = self.client.post("/respondents/search", data={"first_name": "e"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Sending search form failed")

        self.assertTrue(b"pagination" in response.data, "Could not find expected pagination block")

    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_results_page_doesnt_show_pagination_when_not_needed(self, search_respondents_mock):
        self._mock_party_data(search_respondents_mock, 10)
        response = self.client.post("/respondents/search", data={"first_name": "wallis"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Sending search form failed")

        self.assertFalse(b"pagination" in response.data, "Found unexpected pagination block")

    @mock.patch("response_operations_ui.controllers.party_controller.search_respondents")
    def test_search_respondents_page_defaults_to_1(self, search_respondents_mock):
        """Asert that page 1 passed to party controller even though no page specified in passed in params"""
        self._mock_party_data(search_respondents_mock)

        self.client.post("/respondents/search", data={"email_address": "@"}, follow_redirects=True)  # All

        search_respondents_mock.assert_called_with("", "", "@", "1", self.app.config["PARTY_RESPONDENTS_PER_PAGE"])

    @requests_mock.mock()
    def test_delete_respondent_template_for_delete(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_delete_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.put(url_change_respondent_status)
        mock_request.delete(url_auth_respondent_account)
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": True})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)

        get_response = self.client.get(f"respondents/delete-respondent/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("All of the information about this person will be deleted.".encode(), get_response.data)
        self.assertIn("Once their data has been removed, it is unrecoverable.".encode(), get_response.data)
        self.assertIn("Allow 24 hours for this to be completed.".encode(), get_response.data)
        self.assertIn("Delete respondent".encode(), get_response.data)
        post_response = self.client.post(f"respondents/delete-respondent/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(post_response.status_code, 200)
        self.assertIn(
            "The account is pending deletion and will be deleted by the end the day.".encode(), post_response.data
        )

    @requests_mock.mock()
    def test_delete_respondent_template_for_undo_delete(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_delete_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=[])
        get_response = self.client.get(
            f"respondents/undo-delete-respondent/{respondent_party_id}", follow_redirects=True
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn(
            "The account is pending deletion and will be deleted by the end of the day.".encode(), get_response.data
        )
        self.assertIn("Once their data has been removed, it is unrecoverable.".encode(), get_response.data)
        self.assertIn("Reactivate respondent".encode(), get_response.data)
        post_response = self.client.post(
            f"respondents/undo-delete-respondent/{respondent_party_id}", follow_redirects=True
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertIn("Delete respondent".encode(), post_response.data)

    @requests_mock.mock()
    def test_pending_surveys_records_empty(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=[])

        get_response = self.client.get(f"respondents/respondent-details/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Nothing has been shared.".encode(), get_response.data)
        self.assertIn("Nothing has been transferred.".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_records_share_survey(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=share)

        get_response = self.client.get(f"respondents/respondent-details/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(get_response.status_code, 200)
        self.assertNotIn("Nothing has been shared.".encode(), get_response.data)
        self.assertIn("Nothing has been transferred.".encode(), get_response.data)
        self.assertIn("example_four@example.com".encode(), get_response.data)
        self.assertIn("<strong>Bolts and Ratchets Ltd:</strong>BLOCKS</br>".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_records_share_transfer(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=transfer)

        get_response = self.client.get(f"respondents/respondent-details/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Nothing has been shared.".encode(), get_response.data)
        self.assertNotIn("Nothing has been transferred.".encode(), get_response.data)
        self.assertIn("example_four@example.com".encode(), get_response.data)
        self.assertIn("<strong>Bolts and Ratchets Ltd:</strong>BLOCKS</br>".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_resend_email_with_batch_number(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=transfer)
        mock_request.post(url_post_resend_pending_share_email, json={"resend_pending_surveys_email": "success"})
        get_response = self.client.get(
            f"respondents/{respondent_party_id}/pending-surveys/resend-email/{batch_number}", follow_redirects=True
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Nothing has been shared.".encode(), get_response.data)
        self.assertNotIn("Nothing has been transferred.".encode(), get_response.data)
        self.assertIn("example_four@example.com".encode(), get_response.data)
        self.assertIn("<strong>Bolts and Ratchets Ltd:</strong>BLOCKS</br>".encode(), get_response.data)
        self.assertIn("You have successfully resent the [share/transfer] request email.".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_resend_email_with_batch_number_error(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=transfer)
        mock_request.post(url_post_resend_pending_share_email, json={})
        get_response = self.client.get(
            f"respondents/{respondent_party_id}/pending-surveys/resend-email/{batch_number}", follow_redirects=True
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Nothing has been shared.".encode(), get_response.data)
        self.assertNotIn("Nothing has been transferred.".encode(), get_response.data)
        self.assertIn("example_four@example.com".encode(), get_response.data)
        self.assertIn("<strong>Bolts and Ratchets Ltd:</strong>BLOCKS</br>".encode(), get_response.data)
        self.assertIn("Error resending the [share/transfer] request email.".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_delete_confirm_page_for_share(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=share)
        mock_request.post(url_post_resend_pending_share_email, json={})
        get_response = self.client.get(
            f"respondents/{respondent_party_id}/pending-surveys/{batch_number}"
            f"?recipient_email=example_@example.com&is_transfer=False",
            follow_redirects=True,
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Delete sharing request for example_@example.com?".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_delete_confirm_page_for_transfer(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=transfer)
        mock_request.post(url_post_resend_pending_share_email, json={})
        get_response = self.client.get(
            f"respondents/{respondent_party_id}/pending-surveys/{batch_number}"
            f"?recipient_email=example_@example.com&is_transfer=True",
            follow_redirects=True,
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Delete transfer request for example_@example.com?".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_delete_for_share(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=share)
        mock_request.delete(url_post_delete_pending_share)
        get_response = self.client.post(
            f"respondents/{respondent_party_id}/pending-surveys/{batch_number}" f"?is_transfer=False",
            follow_redirects=True,
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("You have successfully deleted the share request.".encode(), get_response.data)

    @requests_mock.mock()
    def test_pending_surveys_delete_for_transfer(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=transfer)
        mock_request.delete(url_post_delete_pending_share)
        get_response = self.client.post(
            f"respondents/{respondent_party_id}/pending-surveys/{batch_number}" f"?is_transfer=True",
            follow_redirects=True,
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("You have successfully deleted the transfer request.".encode(), get_response.data)

    @requests_mock.mock()
    def test_fail_resent_verification_email(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.post(url_resend_verification_email, status_code=500)
        response = self.client.post(f"respondents/resend-verification/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(500, response.status_code)

    @requests_mock.mock()
    def test_get_resent_verification_email(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        response = self.client.get(f"respondents/resend-verification/{respondent_party_id}", follow_redirects=True)
        self.assertEqual(200, response.status_code)

    @requests_mock.mock()
    def test_resent_verification_email(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_respondent_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.post(url_resend_verification_email, status_code=200)
        mock_request.put(url_change_respondent_status)
        mock_request.patch(f"{url_auth_respondent_account}/Jacky.Turner@email.com")
        mock_request.get(f"{url_auth_respondent_account}/Jacky.Turner@email.com", json={"mark_for_deletion": False})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_casegroups_by_business_party_id, json=case_groups)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise)
        mock_request.get(url_get_business_party_by_party_id, json=business_party)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_get_pending_share, json=[])

        response = self.client.post(f"respondents/resend-verification/{respondent_party_id}", follow_redirects=True)

        self.assertEqual(200, response.status_code)
