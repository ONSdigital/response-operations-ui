import unittest

import responses
from flask import current_app

from response_operations_ui import create_app
from response_operations_ui.controllers.cir_controller import get_cir_service_status

TEST_CIR_URL = "http://test.domain"


class TestCaseControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    @responses.activate
    def test_get_cir_service_status_with_gcp_authentication(self):
        with self.app.app_context():
            current_app.config["CIR_API_URL"] = TEST_CIR_URL

            responses.add(
                responses.GET,
                f"{TEST_CIR_URL}/status",
                status=200,
            )

            get_cir_service_status()
