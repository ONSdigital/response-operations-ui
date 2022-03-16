import json
import os

import jwt
import requests_mock

from config import TestingConfig
from tests.views import ViewTestCase

url_sign_in_data = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_surveys = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"
url_permission_url = f"{TestingConfig.UAA_SERVICE_URL}/Users/test-id"
url_uaa_user_list = f"{TestingConfig.UAA_SERVICE_URL}/Users"

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
    uaa_user_list = json.load(fp)
with open(f"{project_root}/test_data/uaa/email_search_user.json") as fp:
    uaa_user_search_email = json.load(fp)


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

    @requests_mock.mock()
    def test_manage_user_accounts_visible_to_user_admin_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        response = self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Manage User Accounts".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_not_visible_to_non_user_admin_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_non_admin_json, status_code=200)
        response = self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Manage User Accounts".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_not_accessible_to_non_user_admin_role(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_non_admin_json, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_manage_user_accounts_403(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json={}, status_code=403)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        response = self.client.get("/admin/manage-user-accounts", follow_redirects=True)

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_manage_user_accounts_success(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_list, status_code=200)
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
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
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
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": ""}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("Please enter a valid email for search".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_email_search_invalid_email(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_search_email, status_code=200)
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})
        form = {"user_search": "test"}
        response = self.client.post("/admin/manage-user-accounts", data=form, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("The email address must be in the correct format".encode(), response.data)

    @requests_mock.mock()
    def test_manage_user_accounts_letter_search_success(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_surveys, json=self.surveys_list_json, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.get(url_uaa_user_list, json=uaa_user_list, status_code=200)
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
