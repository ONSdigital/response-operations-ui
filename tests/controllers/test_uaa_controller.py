import json
import os
import unittest
from urllib.error import HTTPError

import jwt
import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import uaa_controller

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_groups.json") as json_data:
    uaa_user_groups_json = json.load(json_data)

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
url_uaa_get_user_groups = f"{TestingConfig.UAA_SERVICE_URL}/Groups"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"


class TestUAAController(unittest.TestCase):
    def setUp(self):
        payload = {"user_id": user_id, "aud": "response_operations"}
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        self.access_token = jwt.encode(payload, self.app.config["UAA_PRIVATE_KEY"], algorithm="RS256")

    def test_get_user_group_list_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, url_uaa_token, json={"access_token": self.access_token}, status=201)
            rsps.add(
                rsps.GET,
                url_uaa_get_user_groups,
                json=uaa_user_groups_json,
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                groups = uaa_controller.get_user_group_list()
                self.assertIn("7bcaf538-e7fd-4881-9870-71581ce234d2", groups.keys())
                self.assertEqual(groups["7bcaf538-e7fd-4881-9870-71581ce234d2"], "Cooler Group Name for Update")

    def test_get_user_group_list_failure(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, url_uaa_token, json={"access_token": self.access_token}, status=201)
            rsps.add(rsps.GET, url_uaa_get_user_groups, status=400)
            with self.app.app_context():
                self.assertIsNone(uaa_controller.get_user_group_list())
