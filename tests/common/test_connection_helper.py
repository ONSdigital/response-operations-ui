import os
import unittest
from unittest.mock import patch

import requests
import responses

from response_operations_ui import create_app
from response_operations_ui.common.connection_helper import (
    get_response_json_from_service,
)
from response_operations_ui.exceptions.error_codes import ErrorCode
from response_operations_ui.exceptions.exceptions import ExternalApiError

TEST_URL = "http://test.domain"
TARGET_SERVICE = "test"
project_root = os.path.dirname(os.path.dirname(__file__))


class TestConnectionHelper(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.testing = True
        self.client = self.app.test_client()
        responses.reset()  # Clear responses before each test

    @patch("requests.get")
    def test_ApiError_thrown_when_timeout(self, mock_get):
        with self.app.app_context():
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")

            with self.assertRaises(ExternalApiError) as context:
                get_response_json_from_service(TEST_URL, TARGET_SERVICE)
            self.assertEqual(context.exception.error_code, ErrorCode.API_TIMEOUT_ERROR)

    @responses.activate
    def test_ApiError_thrown_when_not_200(self):
        with self.app.app_context():
            responses.add(responses.GET, TEST_URL, status=401)

            with self.assertRaises(ExternalApiError) as context:
                get_response_json_from_service(TEST_URL, TARGET_SERVICE)
            self.assertEqual(context.exception.error_code, ErrorCode.API_UNEXPECTED_STATUS_CODE)

    @responses.activate
    def test_ApiError_thrown_when_404(self):
        with self.app.app_context():
            responses.add(responses.GET, TEST_URL, status=404)

            with self.assertRaises(ExternalApiError) as context:
                get_response_json_from_service(TEST_URL, TARGET_SERVICE)
            self.assertEqual(context.exception.error_code, ErrorCode.NOT_FOUND)

    @responses.activate
    def test_ApiError_thrown_when_content_not_json(self):
        with self.app.app_context():

            responses.add(
                responses.GET,
                TEST_URL,
                status=200,
                body="not_json_despite_content_type_saying_it_is",
                content_type="application/json",
            )

            with self.assertRaises(ExternalApiError) as context:
                get_response_json_from_service(TEST_URL, TARGET_SERVICE)
            self.assertEqual(context.exception.error_code, ErrorCode.API_UNEXPECTED_CONTENT)

    @responses.activate
    def test_ApiError_thrown_when_content_type_not_application_json(self):
        with self.app.app_context():

            responses.add(
                responses.GET,
                TEST_URL,
                status=200,
                body="this_is_plain_text",
                content_type="text/plain",
            )

            with self.assertRaises(ExternalApiError) as context:
                get_response_json_from_service(TEST_URL, TARGET_SERVICE)
            self.assertEqual(context.exception.error_code, ErrorCode.API_UNEXPECTED_CONTENT_TYPE)
