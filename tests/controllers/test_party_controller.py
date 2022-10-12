import json
import os
import unittest
from collections import namedtuple

import mock
import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import party_controller
from response_operations_ui.exceptions.exceptions import (
    ApiError,
    RURetrievalError,
    SearchRespondentsException,
)

fake_response = namedtuple("Response", "status_code json")

ru_ref = "49900000001"
business_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
business_id_2 = "cf3e316a-6644-43b0-a31f-c92b35132b94"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_id_2 = "06cad526-1b1b-41b8-b56b-032e637f0fbd"
sample_summary_id = "1c82f11a-b46a-4944-8ea3-be1ee79571fc"
delete_attributes_by_sample_summary_id_url = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/attributes/sample-summary/{sample_summary_id}"
)
get_business_by_ru_ref_url = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/ref/{ru_ref}"
get_business_by_id_url = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/"
get_survey_by_id_url = f"{TestingConfig.SURVEY_URL}/surveys/"

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/party/get_business_by_ru_ref.json") as fp:
    business_by_ru_ref_json = json.load(fp)
with open(f"{project_root}/test_data/party/business_party.json") as fp:
    business_by_id_json = json.load(fp)
with open(f"{project_root}/test_data/party/business_party_cf3e316a.json") as fp:
    business_by_id_cf3e316a_json = json.load(fp)
with open(f"{project_root}/test_data/party/respondent_party_multiple_associations.json") as fp:
    respondent_json = json.load(fp)
with open(f"{project_root}/test_data/party/get_respondent_enrolments_output.json") as fp:
    expected_enrolments_output = json.load(fp)
with open(f"{project_root}/test_data/survey/survey.json") as fp:
    survey_json = json.load(fp)
with open(f"{project_root}/test_data/survey/survey_06cad526.json") as fp:
    survey_06cad526_json = json.load(fp)


class TestPartyController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_get_respondent_enrolments(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, get_business_by_id_url + business_id, json=business_by_id_json)
            rsps.add(rsps.GET, get_business_by_id_url + business_id_2, json=business_by_id_cf3e316a_json)
            rsps.add(rsps.GET, get_survey_by_id_url + survey_id, json=survey_json)
            rsps.add(rsps.GET, get_survey_by_id_url + survey_id_2, json=survey_06cad526_json)

            with self.app.app_context():
                output = party_controller.get_respondent_enrolments(respondent_json)
            self.assertEqual(output, expected_enrolments_output)

    @mock.patch("requests.get")
    def test_import_search_respondents_raises_error_when_request_to_party_fails(self, requests_mock):
        with self.app.app_context():
            # Mock setups
            requests_mock.return_value = fake_response(status_code=400, json=lambda: [])
            limit = self.app.config["PARTY_RESPONDENTS_PER_PAGE"]
            # Test and assert
            with self.assertRaises(SearchRespondentsException):
                party_controller.search_respondents("firstname", "lastname", "name@email.com", page=1, limit=limit)

    def test_get_respondent_by_party_ids_with_empty_list(self):
        input_data = []
        expected_output = []
        output = party_controller.get_respondent_by_party_ids(input_data)
        self.assertEqual(output, expected_output)

    def test_get_business_by_ru_ref_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, get_business_by_ru_ref_url, json=business_by_ru_ref_json, status=200)

            with self.app.app_context():
                expected = business_by_ru_ref_json
                actual = party_controller.get_business_by_ru_ref(ru_ref)
                self.assertEqual(expected, actual)

    def test_get_business_by_ru_ref_not_found(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, get_business_by_ru_ref_url, status=404)

            with self.app.app_context():
                with self.assertRaises(RURetrievalError):
                    party_controller.get_business_by_ru_ref(ru_ref)

    def test_delete_attributes_by_sample_summary_id_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.DELETE, delete_attributes_by_sample_summary_id_url, status=500)

            with self.app.app_context():
                with self.assertRaises(ApiError):
                    party_controller.delete_attributes_by_sample_summary_id(sample_summary_id)
