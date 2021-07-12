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
    SearchRespondentsException,
)

fake_response = namedtuple("Response", "status_code json")

ru_ref = "49900000001"
get_business_by_ru_ref_url = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/ref/{ru_ref}"

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/party/get_business_by_ru_ref.json") as fp:
    business_by_ru_ref_json = json.load(fp)


class TestPartyController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def tearDown(self):
        pass

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
                with self.assertRaises(ApiError):
                    party_controller.get_business_by_ru_ref(ru_ref)
