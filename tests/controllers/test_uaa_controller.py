import json
import os
import unittest

import jwt
import requests_mock
from requests import HTTPError

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import uaa_controller

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/delete_user_success_response.json") as json_data:
    delete_success_response = json.load(json_data)

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
group_id = "9da7cfd5-95d0-455b-9005-02ce638e56c9"
fake_group_id = "eaf2988b-99b4-423b-9a09-63b1d6f07677"
fake_user_id = "56e97a1b-2188-4989-8342-199b83c505ce"
url_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_uaa_add_to_group = f"{TestingConfig.UAA_SERVICE_URL}/Groups/{group_id}/members"
url_uaa_remove_from_group = f"{TestingConfig.UAA_SERVICE_URL}/Groups/{group_id}/members/{user_id}"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"

uaa_group_add_success_json = {"type": "USER", "value": user_id}
uaa_group_remove_success_json = uaa_group_add_success_json


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

    @requests_mock.mock()
    def test_add_group_membership_success(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.post(url_uaa_add_to_group, json=uaa_group_add_success_json, status_code=201)
        with self.app.test_request_context():
            self.assertEqual(uaa_controller.add_group_membership(user_id, group_id), uaa_group_add_success_json)

    @requests_mock.mock()
    def test_add_group_membership_not_found(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.post(f"{TestingConfig.UAA_SERVICE_URL}/Groups/{fake_group_id}/members", status_code=404)
        with self.app.test_request_context():
            with self.assertRaises(HTTPError):
                uaa_controller.add_group_membership(user_id, fake_group_id)

    @requests_mock.mock()
    def test_remove_group_membership_success(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.delete(url_uaa_remove_from_group, json=uaa_group_add_success_json, status_code=200)
        with self.app.test_request_context():
            self.assertEqual(uaa_controller.remove_group_membership(user_id, group_id), uaa_group_remove_success_json)

    @requests_mock.mock()
    def test_remove_group_membership_not_found(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.delete(
            f"{TestingConfig.UAA_SERVICE_URL}/Groups/{group_id}/members/{fake_user_id}", status_code=404
        )
        with self.app.test_request_context():
            with self.assertRaises(HTTPError):
                uaa_controller.remove_group_membership(fake_user_id, group_id)

    @requests_mock.mock()
    def test_delete_user_success(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.delete(url_uaa_user_by_id, json=delete_success_response, status_code=200)
        with self.app.test_request_context():
            self.assertEqual(uaa_controller.delete_user(user_id), delete_success_response)

    @requests_mock.mock()
    def test_delete_user_not_found(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.delete(url_uaa_user_by_id, status_code=404)
        with self.app.test_request_context():
            with self.assertRaises(HTTPError):
                uaa_controller.delete_user(user_id)
