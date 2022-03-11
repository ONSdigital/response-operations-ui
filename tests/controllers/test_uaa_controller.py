import json
import os
import unittest

import jwt
import requests_mock

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import uaa_controller

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
url_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"


class TestUAAController(unittest.TestCase):
    def setUp(self):
        payload = {"user_id": user_id, "aud": "response_operations"}
        self.app = create_app("TestingConfig")
        self.access_token = jwt.encode(payload, self.app.config["UAA_PRIVATE_KEY"], algorithm="RS256")
        self.client = self.app.test_client()

    @requests_mock.mock()
    def test_user_has_permission_true(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        with self.app.test_request_context():
            self.assertTrue(uaa_controller.user_has_permission("oauth.approvals", user_id))

    @requests_mock.mock()
    def test_user_has_permission_false(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        with self.app.test_request_context():
            self.assertFalse(uaa_controller.user_has_permission("oauth.disapprovals", user_id))

    def test_user_has_permission_rba_disabled(self):
        self.app.config["IS_ROLE_BASED_ACCESS_ENABLED"] = False
        with self.app.test_request_context():
            self.assertTrue(uaa_controller.user_has_permission("surveys.edit", user_id))
