import json
import unittest
from unittest.mock import patch

import requests
import responses
from flask import current_app
from google.auth.exceptions import GoogleAuthError

from response_operations_ui import create_app
from response_operations_ui.controllers.cir_controller import get_cir_service_status
from response_operations_ui.exceptions.error_codes import ErrorCode
from response_operations_ui.exceptions.exceptions import ExternalApiError

TEST_CIR_URL = "http://test.domain"


class TestCIRControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.testing = True
        self.client = self.app.test_client()
        responses.reset()  # Clear responses before each test

    @responses.activate
    def test_get_cir_service_status(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=200,
                body=json.dumps({"status": "OK", "version": "development"}).encode("utf-8"),
                content_type="application/json",
            )

            response_json = get_cir_service_status()
            self.assertEqual(response_json, {"status": "OK", "version": "development"})

    @patch("response_operations_ui.controllers.cir_controller.fetch_and_apply_oidc_credentials")
    def test_GoogleAuthError_thrown_when_fetching_oidc_credentials(self, mock_fetch_and_apply_oidc_credentials):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            mock_fetch_and_apply_oidc_credentials.side_effect = GoogleAuthError("OIDC credentials error")

            with self.assertRaises(ExternalApiError) as context:
                get_cir_service_status()
            self.assertEqual(context.exception.error_code, ErrorCode.API_OIDC_CREDENTIALS_ERROR)

    @patch("requests.Session.get")
    def test_ApiError_thrown_when_connection_error(self, mock_get):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            mock_get.side_effect = requests.ConnectionError("Connection error")

            with self.assertRaises(ExternalApiError) as context:
                get_cir_service_status()
            self.assertEqual(context.exception.error_code, ErrorCode.API_CONNECTION_ERROR)

    @responses.activate
    def test_ApiError_thrown_when_not_200(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=401,
            )

            with self.assertRaises(ExternalApiError) as context:
                get_cir_service_status()
            self.assertEqual(context.exception.error_code, ErrorCode.API_UNEXPECTED_STATUS_CODE)

    @responses.activate
    def test_ApiError_thrown_when_content_not_json(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=200,
                body="not_json_despite_content_type_saying_it_is",
                content_type="application/json",
            )

            with self.assertRaises(ExternalApiError) as context:
                get_cir_service_status()
            self.assertEqual(context.exception.error_code, ErrorCode.API_UNEXPECTED_CONTENT)

    @responses.activate
    def test_ApiError_thrown_when_content_type_not_application_json(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=200,
                body="this_is_plain_text",
                content_type="text/plain",
            )

            with self.assertRaises(ExternalApiError) as context:
                get_cir_service_status()
            self.assertEqual(context.exception.error_code, ErrorCode.API_UNEXPECTED_CONTENT_TYPE)
