import json
import os
import re
from random import randint

import fakeredis
import jwt
import requests_mock

from config import TestingConfig
from response_operations_ui import create_app
from tests.views import ViewTestCase
from tests.views.test_admin import url_surveys
from tests.views.test_sign_in import url_sign_in_data

respondent_party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
ru_ref = "50012345678"
collection_exercise_id_1 = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
collection_exercise_id_2 = "9af403f8-5fc5-43b1-9fca-afbd9c65da5c"
iac_1 = "jkbvyklkwj88"
iac_2 = "ljbgg3kgstr4"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
case_id = "10b04906-f478-47f9-a985-783400dd8482"
CONNECTION_ERROR = "Connection error"

url_search_reporting_units = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/search"
get_respondent_by_id_url = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{respondent_party_id}"
url_edit_contact_details = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{respondent_party_id}"
url_post_case_event = f"{TestingConfig.CASE_URL}/cases/{case_id}/events"
url_change_enrolment_status = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/change_enrolment_status"
url_change_respondent_status = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/edit-account-status/" f"{respondent_party_id}"
)

url_get_business_by_ru_ref = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/ref/reporting-unit-only/{ru_ref}"
url_get_cases_by_business_party_id = f"{TestingConfig.CASE_URL}/cases/partyid/{business_party_id}"

url_get_collection_exercise_by_id = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_get_business_attributes = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}/attributes"
url_get_respondents_by_survey_and_business_id = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/survey_id/{survey_id}/business_id/{business_party_id}"
)
url_get_survey_by_id = f"{TestingConfig.SURVEY_URL}/surveys/{survey_id}"
url_get_respondent_party_by_party_id = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{respondent_party_id}"
url_get_respondent_party_by_list = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents?id={respondent_party_id}"
url_get_iac = f"{TestingConfig.IAC_URL}/iacs"
url_get_case = f"{TestingConfig.CASE_URL}/cases/{case_id}?iac=true"

url_permission_url = f"{TestingConfig.UAA_SERVICE_URL}/Users/test-id"

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/reporting_units/respondent.json") as fp:
    respondent = json.load(fp)
with open(f"{project_root}/test_data/reporting_units/respondent_with_pending_email.json") as fp:
    respondent_with_pending_email = json.load(fp)
with open(f"{project_root}/test_data/case/case.json") as fp:
    case = json.load(fp)

with open(f"{project_root}/test_data/party/business_reporting_unit.json") as fp:
    business_reporting_unit = json.load(fp)
with open(f"{project_root}/test_data/party/business_reporting_unit_no_enrolments.json") as fp:
    business_reporting_unit_no_enrolments = json.load(fp)
with open(f"{project_root}/test_data/case/cases_list.json") as fp:
    cases_list = json.load(fp)
with open(f"{project_root}/test_data/case/cases_list_completed.json") as fp:
    cases_list_completed = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list.json") as fp:
    case_groups = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as fp:
    collection_exercise = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise_2.json") as fp:
    collection_exercise_2 = json.load(fp)
with open(f"{project_root}/test_data/party/business_party.json") as fp:
    business_party = json.load(fp)
with open(f"{project_root}/test_data/party/business_attributes.json") as fp:
    business_attributes = json.load(fp)
with open(f"{project_root}/test_data/case/case_group_statuses.json") as fp:
    case_group_statuses = json.load(fp)
with open(f"{project_root}/test_data/survey/single_survey.json") as fp:
    survey = json.load(fp)
with open(f"{project_root}/test_data/party/respondent_party.json") as fp:
    respondent_party = json.load(fp)
with open(f"{project_root}/test_data/party/respondent_party_list.json") as fp:
    respondent_party_list = json.load(fp)
with open(f"{project_root}/test_data/party/enrolled_respondents.json") as fp:
    enrolled_respondents = json.load(fp)
with open(f"{project_root}/test_data/iac/iac.json") as fp:
    iac = json.load(fp)
with open(f"{project_root}/test_data/iac/iac_inactive.json") as fp:
    iac_inactive = json.load(fp)

user_permission_admin_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "users.admin", "type": "DIRECT"}],
}

user_permission_reporting_unit_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "reportingunits.edit", "type": "DIRECT"}],
}


class TestReportingUnits(ViewTestCase):
    def setup_data(self):
        self.app = create_app("TestingConfig")
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.client = self.app.test_client()
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.surveys_list_json = [
            {
                "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
                "shortName": "ASHE",
                "longName": "ASHE long name",
                "surveyRef": "123",
            }
        ]

    @requests_mock.mock()
    def test_get_reporting_unit(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)
        self.assertIn("221 BLOCKS".encode(), response.data)
        self.assertIn("Not started".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_party_ru_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_party_ru_before_go_live(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, status_code=400)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history

        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "This reporting unit has been loaded using a sample, but the collection exercise is not yet "
            "ready for live.".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_get_reporting_unit_cases_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_cases_404(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, status_code=404)
        mock_request.get(url_get_business_attributes, json={})
        mock_request.get(url_get_respondent_party_by_list, json=[])

        response = self.client.get("/reporting-units/50012345678")

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_reporting_unit_collection_exercise_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", status_code=500)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_party_id_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_survey_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_survey_by_id, status_code=500)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_respondent_party_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_respondent_party_by_party_id, status_code=500)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87", follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_survey_max_no_of_cases_0_causes_warning(self, mock_request):
        """
        If the max-number-of-cases url parameter is 0 then a flashed warning will be displayed saying that it'll use
        the default value instead.
        """
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_reporting_unit_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondents_by_survey_and_business_id, json=enrolled_respondents)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_permission_url, json=user_permission_reporting_unit_edit_json, status_code=200)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87?max-number-of-cases=0",
            follow_redirects=True,
        )

        self.assertIn("Maximum number of cases cannot be 0.  Using default maximum instead".encode(), response.data)
        self.assertIn("Back to surveys".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_reporting_unit_survey_reporting_unit_edit_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_reporting_unit_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondents_by_survey_and_business_id, json=enrolled_respondents)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_permission_url, json=user_permission_reporting_unit_edit_json, status_code=200)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87", follow_redirects=True
        )

        self.assertIn('id="change-enrolment-status"'.encode(), response.data)
        self.assertIn('id="unused-enrolment-code"'.encode(), response.data)
        self.assertIn("Change".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_reporting_unit_survey_enrolment_code_hyperlink(self, mock_request):
        # Set up a business with two collection exercises and no registered respondents or active IACs
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_reporting_unit_edit_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit_no_enrolments)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(url_get_respondents_by_survey_and_business_id, json=enrolled_respondents)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac_inactive)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac_inactive)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87", follow_redirects=True
        )

        enrolment_code_hyperlink = (
            "/reporting-units/50012345678/new_enrolment_code?"
            "case_id=10b04906-f478-47f9-a985-783400dd8482&amp;"
            "collection_exercise_id=9af403f8-5fc5-43b1-9fca-afbd9c65da5c&amp;"
            "ru_name=Bolts+and+Ratchets+Ltd&amp;"
            "trading_as=Bolts+and+Ratchets+Ltd&amp;"
            "survey_ref=221&amp;"
            "survey_name=BLOCKS"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(enrolment_code_hyperlink.encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_survey_no_reporting_unit_edit_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_respondents_by_survey_and_business_id, json=enrolled_respondents)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87", follow_redirects=True
        )

        self.assertNotIn('id="change-enrolment-status"'.encode(), response.data)
        self.assertNotIn('id="unused-enrolment-code"'.encode(), response.data)
        self.assertNotIn("Change".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_reporting_unit_iac_fail(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_respondents_by_survey_and_business_id, json=enrolled_respondents)

        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", status_code=500)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87", follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 7)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_reporting_unit_iac_404(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", status_code=404)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_hides_change_link_when_no_available_statuses(self, mock_request):
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list_completed)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)

        response = self.client.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("ChaFnge</a>".encode(), response.data)

    @requests_mock.mock()
    def test_search_reporting_units_for_1_business_redirects_and_holds_correct_data(self, mock_request):
        mock_business_search_response = {"businesses": [{"name": "test", "ruref": "123456"}], "total_business_count": 2}
        mock_request.get(url_search_reporting_units, json=mock_business_search_response)

        response = self.client.post("/reporting-units", follow_redirects=True)

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
    def test_search_reporting_units_show_correct_pagination_data(self, mock_request):
        mock_business_search_response = TestReportingUnits._build_test_ru_search_response_data(75)

        mock_request.get(url_search_reporting_units, json=mock_business_search_response)

        form_data = {"query": ""}
        response = self.client.post("/reporting-units", data=form_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        data = re.sub("<[^<]+?>", "", response.data.decode())  # Strip out html tags from the response data
        self.assertIn("75 Results found", data)
        self.assertIn("Displaying 1 - 25 of 75", data)
        self.assertIn("Page 1 of 3", data)  # Validates the page count is correct
        data = data.replace("\n", "").replace(" ", "")  # Need to remove newline and space due to ONS formatting
        self.assertIn("123Next", data)  # Validates Pagination controls displayed

    @requests_mock.mock()
    def test_search_reporting_units_no_results_displays_correctly(self, mock_request):
        mock_business_search_response = {"businesses": [], "total_business_count": 0}

        mock_request.get(url_search_reporting_units, json=mock_business_search_response)

        form_data = {"query": ""}
        response = self.client.post("/reporting-units", data=form_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        data = re.sub("<[^<]+?>", "", response.data.decode())  # Strip out html tags from the response data
        self.assertIn("No results found", data)

    @requests_mock.mock()
    def test_search_reporting_units_for_specific_name_displays_correctly(self, mock_request):
        ru_ref_num = "12345678901"  # named so as to not clash with outer definition of ru_ref
        mock_response = {"businesses": [{"name": "SomeName", "ruref": ru_ref_num}], "total_business_count": 1}

        mock_request.get(url_search_reporting_units, json=mock_response)

        form_data = {"query": "SomeName"}
        response = self.client.post("/reporting-units", data=form_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        data = response.data.decode()
        self.assertIn("1 Result found", data)
        self.assertIn('value="SomeName"', data)  # Validates that search term is displayed in text entry box

        # now validate that the ru is displayed as an href
        self.assertIn(f'href="/reporting-units/{ru_ref_num}" name="details-link-{ru_ref_num}">{ru_ref_num}', data)

    @requests_mock.mock()
    def test_resend_verification_email(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent)
        response = self.client.get(f"reporting-units/resend_verification/50012345678/{respondent_party_id}")
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_resend_verification_email_to_pending_email_address(self, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent_with_pending_email)
        response = self.client.get(f"reporting-units/resend_verification/50012345678/{respondent_party_id}")
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_change_respondent_status(self, mock_request):
        mock_request.put(url_change_respondent_status)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)

        response = self.client.post(
            f"reporting-units/50012345678/change-respondent-status"
            f"?respondent_id={respondent_party_id}&change_flag=ACTIVE",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_change_respondent_status_fail(self, mock_request):
        mock_request.put(url_change_respondent_status, status_code=500)

        response = self.client.post(
            f"reporting-units/50012345678/change-respondent-status"
            f"?respondent_id={respondent_party_id}&change_flag=ACTIVE",
            follow_redirects=True,
        )
        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_confirm_change_respondent_status(self, mock_request):
        mock_request.get(get_respondent_by_id_url)
        mock_request.put(url_change_respondent_status)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)

        response = self.client.get(
            f"reporting-units/50012345678/change-respondent-status"
            f"?party_id={respondent_party_id}&change_flag=ACTIVE&tab=reporting_units",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

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

        response = self.client.get(
            f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}", follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_edit_contact_details(self, mock_request):
        changed_details = {
            "first_name": "Tom",
            "last_name": "Smith",
            "email": "Jacky.Turner@email.com",
            "telephone": "7971161867",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_edit_contact_details_email_failures(self, mock_request):
        changed_details = {
            "first_name": "Tom",
            "last_name": "Smith",
            "email": "Jacky.Turner@email.com",
            "telephone": "7971161859",
        }
        mock_request.get(get_respondent_by_id_url, json=respondent)

        # User already exists (409)
        mock_request.put(url_edit_contact_details, status_code=409)
        response = self.client.post(
            f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
            data=changed_details,
            follow_redirects=True,
        )
        self.assertIn("Error - email address already exists".encode(), response.data)

        # User not found (404)
        mock_request.put(url_edit_contact_details, status_code=404)
        response = self.client.post(
            f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
            data=changed_details,
            follow_redirects=True,
        )

        self.assertIn(CONNECTION_ERROR.encode(), response.data)

        # Server error (500)
        mock_request.put(url_edit_contact_details, status_code=500)
        response = self.client.post(
            f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
            data=changed_details,
            follow_redirects=True,
        )
        self.assertIn(CONNECTION_ERROR.encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_last_name_change(self, mock_request):
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Smith",
            "email": "Jacky.Turner@email.com",
            "telephone": "7971161859",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    def mock_for_change_details(self, changed_details, mock_request):
        mock_request.get(get_respondent_by_id_url, json=respondent)
        mock_request.put(url_edit_contact_details)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        response = self.client.post(
            f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
            data=changed_details,
            follow_redirects=True,
        )
        return response

    @requests_mock.mock()
    def test_edit_contact_details_telephone_change(self, mock_request):
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Turner",
            "email": "Jacky.Turner@email.com",
            "telephone": "7971161867",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_edit_contact_details_email_change(self, mock_request):
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Turner",
            "email": "Jacky.Turner@thisemail.com",
            "telephone": "7971161859",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_edit_contact_details_email_change_with_trailing_space(self, mock_request):
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Turner",
            "email": r"Jacky.Turner@thisemail.com ",
            "telephone": "7971161859",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNot(r"Jacky.Turner@thisemail.com ".encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_and_email_change(self, mock_request):
        changed_details = {
            "first_name": "Jacky",
            "last_name": "Turner",
            "email": "Jacky.Turner@thisemail.com",
            "telephone": "7971161867",
        }
        response = self.mock_for_change_details(changed_details, mock_request)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code(self, mock_request):
        mock_request.post(url_post_case_event)
        mock_request.get(url_get_case, json=case)

        response = self.client.get(
            f"/reporting-units/{ru_ref}/new_enrolment_code?case_id={case['id']}&"
            "survey_name=test_survey_name&trading_as=trading_name&ru_name=test_ru_name",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("jkbvyklkwj88".encode(), response.data)
        self.assertIn("test_ru_name".encode(), response.data)
        self.assertIn("trading_name".encode(), response.data)
        self.assertIn("test_survey_name".encode(), response.data)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code_event_fail(self, mock_request):
        mock_request.post(url_post_case_event, status_code=500)

        response = self.client.get(
            f"/reporting-units/{ru_ref}/new_enrolment_code?case_id={case['id']}", follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code_case_fail(self, mock_request):
        mock_request.post(url_post_case_event)
        mock_request.get(url_get_case, status_code=500)

        response = self.client.get(
            f"/reporting-units/{ru_ref}/new_enrolment_code?case_id={case['id']}&"
            "survey_name=test_survey_name&trading_as=trading_name&ru_name=test_ru_name",
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    def test_disable_enrolment_view(self):
        response = self.client.get(
            "/reporting-units/ru_ref/change-enrolment-status"
            "?survey_id=test_id&survey_name=test_survey_name&respondent_id=test_id"
            "&respondent_first_name=first_name&respondent_last_name=last_name"
            "&business_id=test_id"
            "&trading_as=test_name&change_flag=DISABLED"
            "&ru_name=test_ru_name&tab=reporting_units"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_ru_name".encode(), response.data)
        self.assertIn("test_name".encode(), response.data)
        self.assertIn("test_survey_name".encode(), response.data)
        self.assertIn("first_name".encode(), response.data)
        self.assertIn("Disable enrolment".encode(), response.data)

    @requests_mock.mock()
    def test_disable_enrolment_post(self, mock_request):
        mock_request.put(url_change_enrolment_status)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)

        response = self.client.post(
            "/reporting-units/50012345678/change-enrolment-status"
            "?survey_id=test_id&respondent_id=test_id&business_id=test_id&change_flag=DISABLED",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)

    @requests_mock.mock()
    def test_disable_enrolment_post_fail(self, mock_request):
        mock_request.put(url_change_enrolment_status, status_code=500)

        response = self.client.post(
            "/reporting-units/50012345678/change-enrolment-status"
            "?survey_id=test_id&respondent_id=test_id&business_id=test_id&change_flag=DISABLED",
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_reporting_unit_page_no_message_edit_permission(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_cases_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_respondent_party_by_party_id, json=respondent_party)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondents_by_survey_and_business_id, json=enrolled_respondents)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)

        response = self.client.get(
            "/reporting-units/50012345678/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87", follow_redirects=True
        )

        self.assertNotIn("Create message".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @staticmethod
    def _build_test_ru_search_response_data(count):
        businesses = [{"name": f"{i}_name", "ruref": f"{randint(0, 100000000000)}"} for i in range(count)]
        return {"businesses": businesses, "total_business_count": count}
