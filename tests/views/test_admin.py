import json
import os
from unittest.mock import patch

import jwt
import requests_mock

from config import TestingConfig
from tests.views import ViewTestCase

url_sign_in_data = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_surveys = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"
url_permission_url = f"{TestingConfig.UAA_SERVICE_URL}/Users/test-id"
url_uaa_user_list = f"{TestingConfig.UAA_SERVICE_URL}/Users"

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
url_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_invalid_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/adb544bb-5e60-46e0-b2f0-285e0acee6fd"

user_permission_non_admin_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "uaa.user", "type": "DIRECT"}],
}

user_permission_admin_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "users.admin", "type": "DIRECT"}],
}

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_list.json") as fp:
    uaa_user_list_json = json.load(fp)
with open(f"{project_root}/test_data/uaa/email_search_user.json") as fp:
    uaa_user_search_email = json.load(fp)
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)


class TestMessage(ViewTestCase):
    def setup_data(self):
        self.surveys_list_json = [
            {
                "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
                "shortName": "ASHE",
                "longName": "ASHE long name",
                "surveyRef": "123",
            }
        ]
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")

    def setup_common_mocks(self, mock_request, with_uaa_user_list=False):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        if with_uaa_user_list:
            mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        return mock_request

    @requests_mock.mock()
    def test_manage_user_accounts_visible_to_user_admin_role(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        response = self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Online Business Surveys".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_not_visible_to_non_user_admin_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_non_admin_json, status_code=200)
        response = self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Manage user accounts".encode(), response.data)
        self.assertIn("Online Business Surveys".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_not_accessible_to_non_user_admin_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_non_admin_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Manage user accounts".encode(), response.data)
        self.assertIn("Online Business Surveys".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_403(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_uaa_user_list, json={}, status_code=403)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Failed to retrieve user list, please try again".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)
        self.assertIn("Andy0".encode(), response.data)
        self.assertIn("Johnson".encode(), response.data)
        self.assertIn("Edit or delete user account".encode(), response.data)
        self.assertIn("Andy0.Smith@ons.gov.uk".encode(), response.data)
        self.assertIn("Page 1 of 26".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_email_search(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": "Andy155.Smith@ons.gov.uk"}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)
        self.assertNotIn("Andy0".encode(), response.data)
        self.assertNotIn("Johnson".encode(), response.data)
        self.assertIn("Edit or delete user account".encode(), response.data)
        self.assertNotIn("Andy0.Smith@ons.gov.uk".encode(), response.data)
        self.assertNotIn("Page 1 of 26".encode(), response.data)
        self.assertIn("Andy155.Smith@ons.gov.uk".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_email_search_no_email(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": ""}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Please enter a valid email for search".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_email_search_invalid_email(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": "test"}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("The email address must be in the correct format".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_letter_search_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": "test"}
        response = self.client.get("/admin/manage-user-accounts?user_with_email=C", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)
        self.assertIn("Andy0".encode(), response.data)
        self.assertIn("Johnson".encode(), response.data)
        self.assertIn("Edit or delete user account".encode(), response.data)
        self.assertIn("Andy0.Smith@ons.gov.uk".encode(), response.data)
        self.assertIn("Page 1 of 26".encode(), response.data)
        self.assertIn("Andy155.Smith@ons.gov.uk".encode(), response.data)

    # Edit user permission
    @requests_mock.mock()
    def test_edit_account_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get(f"/admin/manage-account/{user_id}", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Select user permissions".encode(), response.data)
        self.assertIn("ONS User".encode(), response.data)
        self.assertIn("Delete user account".encode(), response.data)

        # Check we're not
        self.assertNotIn("Create new user account".encode(), response.data)
        self.assertNotIn("Edit or delete user account".encode(), response.data)

    @requests_mock.mock()
    def test_edit_account_get_fail_own_id(self, mock_request):
        payload = {"user_id": user_id, "aud": "response_operations"}
        own_id_access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        mock_request.post(url_sign_in_data, json={"access_token": own_id_access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get(f"/admin/manage-account/{user_id}", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("You cannot modify your own user account".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

    @requests_mock.mock()
    def test_edit_account_get_fail_user_not_found(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_invalid_uaa_user_by_id, status_code=404)

        # uuid for this user doesn't exist
        response = self.client.get("/admin/manage-account/adb544bb-5e60-46e0-b2f0-285e0acee6fd", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("Selected user could not be found".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

    @requests_mock.mock()
    def test_edit_account_post_fail_own_id(self, mock_request):
        payload = {"user_id": user_id, "aud": "response_operations"}
        own_id_access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        mock_request.post(url_sign_in_data, json={"access_token": own_id_access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.post(f"/admin/manage-account/{user_id}", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("You cannot modify your own user account".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

    @requests_mock.mock()
    def test_edit_account_post_fail_user_not_found(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_invalid_uaa_user_by_id, status_code=404)

        # uuid for this user doesn't exist
        response = self.client.post("/admin/manage-account/adb544bb-5e60-46e0-b2f0-285e0acee6fd", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("User does not exist".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

    #
    # Delete user
    @requests_mock.mock()
    def test_delete_account_get_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get(f"/admin/manage-account/{user_id}/delete", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Delete ONS User's user account?".encode(), response.data)
        self.assertIn("All the information about ons@ons.fake will be deleted.".encode(), response.data)
        self.assertIn("An email to notify the user will be sent.".encode(), response.data)

    @requests_mock.mock()
    def test_delete_account_get_fail_own_id(self, mock_request):
        payload = {"user_id": user_id, "aud": "response_operations"}
        own_id_access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        mock_request.post(url_sign_in_data, json={"access_token": own_id_access_token}, status_code=201)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        response = self.client.get(f"/admin/manage-account/{user_id}/delete", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("You cannot delete your own user account".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

        # Check we're NOT on the account deletion page
        self.assertNotIn("All the information about ons@ons.fake will be deleted.".encode(), response.data)
        self.assertNotIn("An email to notify the user will be sent.".encode(), response.data)

    @requests_mock.mock()
    def test_delete_account_get_fail_user_not_found(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_invalid_uaa_user_by_id, status_code=404)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        # uuid for this user doesn't exist
        response = self.client.get(
            "/admin/manage-account/adb544bb-5e60-46e0-b2f0-285e0acee6fd/delete", follow_redirects=True
        )
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("User does not exist".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

    @requests_mock.mock()
    def test_delete_account_post_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        with patch("response_operations_ui.views.admin.manage_user_accounts.NotifyController") as mock_notify:
            mock_notify().request_to_notify.return_value = None
            mock_request.delete(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            response = self.client.post(f"/admin/manage-account/{user_id}/delete", follow_redirects=True)
            self.assertIn("Manage user accounts".encode(), response.data)
            self.assertIn("Create new user account".encode(), response.data)
            self.assertIn(
                "User account has been successfully deleted. An email to inform the user has been sent.".encode(),
                response.data,
            )

    @requests_mock.mock()
    def test_delete_account_post_fail_own_id(self, mock_request):
        payload = {"user_id": user_id, "aud": "response_operations"}
        own_id_access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        mock_request.post(url_sign_in_data, json={"access_token": own_id_access_token}, status_code=201)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        response = self.client.post(f"/admin/manage-account/{user_id}/delete", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("You cannot delete your own user account".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)

    @requests_mock.mock()
    def test_delete_account_post_fail_user_not_found(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_invalid_uaa_user_by_id, status_code=404)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        # uuid for this user doesn't exist
        response = self.client.post(
            "/admin/manage-account/adb544bb-5e60-46e0-b2f0-285e0acee6fd/delete", follow_redirects=True
        )
        self.assertEqual(200, response.status_code)
        # Check we're on the account list page with a message flashed
        self.assertIn("User does not exist".encode(), response.data)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)
