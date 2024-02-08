import json
import os
from unittest.mock import patch

import fakeredis
import jwt
import requests_mock

from config import TestingConfig
from tests.views import ViewTestCase

group_id = "79f41e0c-9991-4ee8-b2d0-af2f470dfd20"
url_sign_in_data = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_surveys = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"
url_permission_url = f"{TestingConfig.UAA_SERVICE_URL}/Users/test-id"
url_uaa_groups = f"{TestingConfig.UAA_SERVICE_URL}/Groups"
url_uaa_users = f"{TestingConfig.UAA_SERVICE_URL}/Users"
url_uaa_add_to_group = f"{TestingConfig.UAA_SERVICE_URL}/Groups/{group_id}/members"

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
user_email = "some.one@ons.gov.uk"
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
with open(f"{project_root}/test_data/uaa/get_groups_success.json") as json_data:
    get_groups_success_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/create_user_success.json") as json_data:
    create_user_success_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/create_user_already_exists.json") as json_data:
    create_user_already_exists_json = json.load(json_data)

uaa_group_add_success_json = {"type": "USER", "value": user_id}


class TestMessage(ViewTestCase):
    def setup_data(self):
        self.surveys_list_json = [
            {
                "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
                "shortName": "ASHE",
                "longName": "ASHE long name",
                "surveyRef": "123",
                "surveyMode": "EQ",
            }
        ]
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

    def setup_common_mocks(self, mock_request, with_uaa_user_list=False):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        if with_uaa_user_list:
            mock_request.get(url_uaa_users, json=uaa_user_search_email, status_code=200)
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
        self.assertIn(
            "You do not have the required permission to "
            "access this function under your current role profile".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_manage_user_accounts_403(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_uaa_users, json={}, status_code=403)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Failed to retrieve user list, please try again".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_uaa_users, json=uaa_user_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)
        self.assertIn("Andy0".encode(), response.data)
        self.assertIn("Johnson".encode(), response.data)
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Delete".encode(), response.data)
        self.assertIn("Andy0.Smith@ons.gov.uk".encode(), response.data)
        self.assertIn("Page 1 of 26".encode(), response.data)
        # Validates Pagination controls displayed
        self.assertIn('<a href="?page=1" class="ons-pagination__link"aria-current="true" aria-label="Current page ('
                      'Page 1 of 26)">1</a>'.encode(), response.data)  
        self.assertIn('<a href="?page=2" class="ons-pagination__link"aria-label="Go to page 2"rel="next">2</a>'.encode(), response.data)  # Validates Pagination controls displayed

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
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Delete".encode(), response.data)
        self.assertNotIn("Andy0.Smith@ons.gov.uk".encode(), response.data)
        self.assertNotIn("Page 1 of 26".encode(), response.data)
        self.assertIn("Andy155.Smith@ons.gov.uk".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_email_search_failure(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        # No email address
        form = {"user_search": ""}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Please enter a valid email for search".encode(), response.data)

        # Invalid email address
        form = {"user_search": "test"}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("The email address must be in the correct format".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_letter_search_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_uaa_users, json=uaa_user_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": "test"}
        response = self.client.get("/admin/manage-user-accounts?user_with_email=C", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Manage user accounts".encode(), response.data)
        self.assertIn("Create new user account".encode(), response.data)
        self.assertIn("Andy0".encode(), response.data)
        self.assertIn("Johnson".encode(), response.data)
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Delete".encode(), response.data)
        self.assertIn("Andy0.Smith@ons.gov.uk".encode(), response.data)
        self.assertIn("Page 1 of 26".encode(), response.data)
        self.assertIn("Andy155.Smith@ons.gov.uk".encode(), response.data)

    # Create account

    @requests_mock.mock()
    def test_get_create_account_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/admin/create-account", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Create your account".encode(), response.data)
        self.assertIn("Manager permissions".encode(), response.data)
        self.assertIn("Create account".encode(), response.data)

    @requests_mock.mock()
    def test_post_create_account_success(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        mock_request.get(url_uaa_groups, json=get_groups_success_json, status_code=200)
        mock_request.post(url_uaa_users, json=create_user_success_json, status_code=200)
        mock_request.post(url_uaa_add_to_group, json=uaa_group_add_success_json, status_code=201)
        with patch("response_operations_ui.views.admin.manage_user_accounts.NotifyController") as mock_notify:
            mock_notify().request_to_notify.return_value = None
            response = self.client.post(
                "/admin/create-account",
                follow_redirects=True,
                data={"first_name": "ONS", "last_name": "user", "email": user_email, "surveys_edit": True},
            )
            self.assertEqual(200, response.status_code)
            self.assertIn(f"An email to activate the account has been sent to {user_email}.".encode(), response.data)
            self.assertIn("This email will be valid for 4 weeks.".encode(), response.data)
            self.assertIn("Return to manage user accounts".encode(), response.data)

    @requests_mock.mock()
    def test_post_create_account_failure(self, mock_request):
        mock_request = self.setup_common_mocks(mock_request, with_uaa_user_list=True)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        mock_request.get(url_uaa_groups, status_code=403)

        # Test getting group failure
        response = self.client.post(
            "/admin/create-account",
            follow_redirects=True,
            data={"first_name": "ONS", "last_name": "user", "email": user_email, "surveys_edit": True},
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Create your account".encode(), response.data)
        self.assertIn("Manager permissions".encode(), response.data)
        self.assertIn("Create account".encode(), response.data)
        self.assertIn("Failed to get groups, please try again".encode(), response.data)

        # Test creating user failure
        mock_request.get(url_uaa_groups, json=get_groups_success_json, status_code=200)
        mock_request.post(url_uaa_users, json=create_user_already_exists_json, status_code=409)
        response = self.client.post(
            "/admin/create-account",
            follow_redirects=True,
            data={"first_name": "ONS", "last_name": "user", "email": user_email, "surveys_edit": True},
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Create your account".encode(), response.data)
        self.assertIn("Manager permissions".encode(), response.data)
        self.assertIn("Create account".encode(), response.data)
        self.assertIn(f"Username already in use: {user_email}".encode(), response.data)
        self.assertNotIn("Failed to get groups, please try again".encode(), response.data)

        # Test adding group membership failure
        mock_request.get(url_uaa_groups, json=get_groups_success_json, status_code=200)
        mock_request.post(url_uaa_users, json=create_user_success_json, status_code=200)
        mock_request.post(url_uaa_add_to_group, status_code=400)
        with patch("response_operations_ui.views.admin.manage_user_accounts.NotifyController") as mock_notify:
            mock_notify().request_to_notify.return_value = None
            response = self.client.post(
                "/admin/create-account",
                follow_redirects=True,
                data={"first_name": "ONS", "last_name": "user", "email": user_email, "surveys_edit": True},
            )
            self.assertEqual(200, response.status_code)
            self.assertIn(f"An email to activate the account has been sent to {user_email}.".encode(), response.data)
            self.assertIn("This email will be valid for 4 weeks.".encode(), response.data)
            self.assertIn(
                "Failed to give the user the surveys_edit permission. The account has still been created but "
                "the permission will need to be granted later".encode(),
                response.data,
            )
            self.assertIn("Return to manage user accounts".encode(), response.data)

            # Verify previous flash messages are not here, and that we're on the confirmation screen as failing to add
            # to a group won't stop the creation journey.
            self.assertNotIn("Create your account".encode(), response.data)
            self.assertNotIn("Manager permissions".encode(), response.data)
            self.assertNotIn(f"Username already in use: {user_email}".encode(), response.data)
            self.assertNotIn("Failed to get groups, please try again".encode(), response.data)

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

        # Check we're not on manage account page
        self.assertNotIn("Create new user account".encode(), response.data)
        self.assertNotIn("First name".encode(), response.data)
        self.assertNotIn("Last name".encode(), response.data)

    @requests_mock.mock()
    def test_edit_account_get_fail_own_id(self, mock_request):
        payload = {"user_id": user_id, "aud": "response_operations"}
        own_id_access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        mock_request.post(url_sign_in_data, json={"access_token": own_id_access_token}, status_code=201)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_users, json=uaa_user_search_email, status_code=200)
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
        mock_request.get(url_uaa_users, json=uaa_user_search_email, status_code=200)
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
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get(f"/admin/manage-account/{user_id}/delete", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Delete ONS User's user account?".encode(), response.data)
        self.assertIn(f"All the information about {user_email} will be deleted.".encode(), response.data)
        self.assertIn("An email to notify the user will be sent.".encode(), response.data)

    @requests_mock.mock()
    def test_delete_account_get_fail_own_id(self, mock_request):
        payload = {"user_id": user_id, "aud": "response_operations"}
        own_id_access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        mock_request.post(url_sign_in_data, json={"access_token": own_id_access_token}, status_code=201)
        mock_request.get(url_uaa_users, json=uaa_user_search_email, status_code=200)
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
        mock_request.get(url_uaa_users, json=uaa_user_search_email, status_code=200)
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
