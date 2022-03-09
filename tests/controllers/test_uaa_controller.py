import json
import os
import unittest
from unittest.mock import patch

from response_operations_ui import create_app
from response_operations_ui.controllers import uaa_controller

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"


class TestUAAController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    @patch("response_operations_ui.controllers.uaa_controller.get_user_by_id")
    def test_user_has_permission(self, mock_get_user):
        mock_get_user.return_value = uaa_user_by_id_json
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        self.assertTrue(uaa_controller.user_has_permission("oauth.approvals"))
        self.assertFalse(uaa_controller.user_has_permission("oauth.disapprovals"))
