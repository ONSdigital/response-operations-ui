import json
import unittest

import responses
from flask import current_app
from requests import HTTPError

from response_operations_ui import create_app
from response_operations_ui.controllers.cir_controller import get_cir_service_status

TEST_CIR_URL = "http://test.domain"


class TestCIRControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    @responses.activate
    def test_get_cir_service_status(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=200,
                body=json.dumps({"status": "ok", "service": "cir"}).encode("utf-8"),
                content_type="application/json",
            )

            response_json = get_cir_service_status()
            self.assertEqual(response_json, {"status": "ok", "service": "cir"})

    @responses.activate
    def test_get_cir_service_status_thows_exception_when_not_json(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=200,
                body="not json despite content_type saying it is",
                content_type="application/json",
            )

            with self.assertRaises(HTTPError):
                get_cir_service_status()

    @responses.activate
    def test_get_cir_service_status_thows_exception_when_not_200(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=404,
            )

            with self.assertRaises(HTTPError):
                get_cir_service_status()
