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
with open(f"{project_root}/test_data/uaa/get_groups_success.json") as json_data:
    get_groups_success_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/create_user_success.json") as json_data:
    create_user_success_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/create_user_already_exists.json") as json_data:
    create_user_already_exists_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/email_search_user.json") as fp:
    uaa_user_search_email = json.load(fp)

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
group_id = "9da7cfd5-95d0-455b-9005-02ce638e56c9"
fake_group_id = "eaf2988b-99b4-423b-9a09-63b1d6f07677"
fake_user_id = "56e97a1b-2188-4989-8342-199b83c505ce"
user_first_name = "Some"
user_last_name = "One"
user_email = "some.one@ons.gov.uk"
user_password = "password"
url_uaa_users = f"{TestingConfig.UAA_SERVICE_URL}/Users"
url_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_uaa_user_by_email = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{user_email}%22"
url_uaa_password_reset_code = f"{TestingConfig.UAA_SERVICE_URL}/password_resets"
url_uaa_password_change = f"{TestingConfig.UAA_SERVICE_URL}/password_change"
url_uaa_groups = f"{TestingConfig.UAA_SERVICE_URL}/Groups"
url_uaa_add_to_group = f"{TestingConfig.UAA_SERVICE_URL}/Groups/{group_id}/members"
url_uaa_remove_from_group = f"{TestingConfig.UAA_SERVICE_URL}/Groups/{group_id}/members/{user_id}"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_update_password = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}/password"
url_uaa_verify_user = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}/verify"

uaa_group_add_success_json = {"type": "USER", "value": user_id}
uaa_group_remove_success_json = uaa_group_add_success_json


class TestUAAController(unittest.TestCase):
    def setUp(self):
        payload = {"user_id": user_id, "aud": "response_operations"}
        self.app = create_app("TestingConfig")
        self.access_token = jwt.encode(payload, self.app.config["UAA_PRIVATE_KEY"], algorithm="RS256")
        self.client = self.app.test_client()

    # user_has_permission
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

    # update_user_password

    @requests_mock.mock()
    def test_update_user_password_user_client_error(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.put(url_uaa_update_password, status_code=400)
        expected_output = {"status_code": 400, "message": "Invalid JSON format or missing fields"}
        with self.app.test_request_context():
            self.assertDictEqual(
                uaa_controller.update_user_password(uaa_user_by_id_json, "old", "new"), expected_output
            )

    @requests_mock.mock()
    def test_update_user_password_user_not_found(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.put(url_uaa_update_password, status_code=404)
        expected_output = {"user_id": ["User id not found"]}
        with self.app.test_request_context():
            self.assertDictEqual(
                uaa_controller.update_user_password(uaa_user_by_id_json, "old", "new"), expected_output
            )

    # add_group_membership

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

    # remove_group_membership

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

    # delete_user

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

    # get_groups

    @requests_mock.mock()
    def test_get_groups_success(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_groups, json=get_groups_success_json, status_code=200)
        with self.app.test_request_context():
            self.assertEqual(uaa_controller.get_groups(), get_groups_success_json)

    @requests_mock.mock()
    def test_get_groups_failure(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_groups, status_code=403)
        with self.app.test_request_context():
            with self.assertRaises(HTTPError):
                uaa_controller.get_groups()

    # create_user_account_with_random_password

    @requests_mock.mock()
    def test_create_user_account_with_random_password_success(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.post(url_uaa_users, json=create_user_success_json, status_code=200)
        with self.app.test_request_context():
            self.assertEqual(
                uaa_controller.create_user_account_with_random_password(user_email, user_first_name, user_last_name),
                create_user_success_json,
            )

    @requests_mock.mock()
    def test_create_user_account_with_random_password_user_already_exists(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.post(url_uaa_users, json=create_user_already_exists_json, status_code=409)
        with self.app.test_request_context():
            self.assertEqual(
                uaa_controller.create_user_account_with_random_password(user_email, user_first_name, user_last_name),
                {"error": "Username already in use: some.one@ons.gov.uk"},
            )

    # change_user_password_by_email

    @requests_mock.mock()
    def test_change_user_password_by_id_user_not_found(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_email, status_code=404)

        with self.app.test_request_context():
            self.assertIsNone(uaa_controller.change_user_password_by_email("some.one@ons.gov.uk", user_password))

    @requests_mock.mock()
    def test_change_user_password_retrieve_code_failure(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_email, json=uaa_user_search_email, status_code=200)
        # Docs aren't clear about failure codes for this endpoint so 500 is a safe one we can assume it can throw.
        mock_request.post(url_uaa_password_reset_code, status_code=500)

        with self.app.test_request_context():
            self.assertIsNone(uaa_controller.change_user_password_by_email(user_email, user_password))

    # change_user_password_by_id

    @requests_mock.mock()
    def test_reset_user_password_by_id_user_not_found(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, status_code=404)

        with self.app.test_request_context():
            self.assertIsNone(uaa_controller.change_user_password_by_id(user_id, user_password))

    @requests_mock.mock()
    def test_reset_user_password_by_id_retrieve_code_failure(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        # Docs aren't clear about failure codes for this endpoint so 500 is a safe one we can assume it can throw.
        mock_request.post(url_uaa_password_reset_code, status_code=500)

        with self.app.test_request_context():
            self.assertIsNone(uaa_controller.change_user_password_by_id(user_id, user_password))

    @requests_mock.mock()
    def test_reset_user_password_by_id_password_change_failure(self, mock_request):
        password_reset_code_json = {"code": "f-Ni-kNixp", "user_id": user_id}
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        mock_request.post(url_uaa_password_reset_code, json=password_reset_code_json, status_code=201)
        mock_request.post(url_uaa_password_change, status_code=500)

        with self.app.test_request_context():
            output = uaa_controller.change_user_password_by_id(user_id, user_password)
            self.assertEqual(output.status_code, 500)

    @requests_mock.mock()
    def test_reset_user_password_by_id_password_change_success(self, mock_request):
        password_reset_code_json = {"code": "f-Ni-kNixp", "user_id": user_id}
        password_change_success_json = {
            "username": user_email,
            "email": user_email,
            "code": "tewO_0M2__",
            "user_id": user_id,
        }
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        mock_request.post(url_uaa_password_reset_code, json=password_reset_code_json, status_code=201)
        mock_request.post(url_uaa_password_change, json=password_change_success_json, status_code=200)

        with self.app.test_request_context():
            output = uaa_controller.change_user_password_by_id(user_id, user_password)
            self.assertEqual(output.status_code, 200)
            self.assertEqual(output.json(), password_change_success_json)
