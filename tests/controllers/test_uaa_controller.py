import json
import os
import unittest
from urllib.error import HTTPError

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import uaa_controller

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_groups.json") as json_data:
    uaa_user_groups_json = json.load(json_data)

url_uaa_get_user_groups = f"{TestingConfig.UAA_SERVICE_URL}/Groups"


class TestUAAController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def test_get_user_group_list_success(self):
        with responses.RequestsMock() as rsps:
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
            rsps.add(rsps.GET, url_uaa_get_user_groups, status=400)
            with self.app.app_context():
                self.assertRaises(HTTPError, uaa_controller.get_user_group_list())
