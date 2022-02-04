import json
import os
import unittest
from unittest import mock
from unittest.mock import patch

import jwt
import requests_mock

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.common import token_decoder

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)
with open(f"{project_root}/test_data/uaa/updated_name.json") as json_data:
    updated_name_json = json.load(json_data)

test_email = "fake@ons.gov.uk"
user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_get_accounts = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{test_email}%22"
url_uaa_get_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_uaa_create_account = f"{TestingConfig.UAA_SERVICE_URL}/Users"
url_uaa_update_name = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"


class TestAccounts(unittest.TestCase):
    def setUp(self):
        payload = {"user_id": user_id, "aud": "response_operations"}
        self.app = create_app("TestingConfig")
        self.access_token = jwt.encode(payload, self.app.config["UAA_PRIVATE_KEY"], algorithm="RS256")
        self.client = self.app.test_client()

    def test_request_account_page(self):
        response = self.client.get("/account/request-new-account")
        self.assertIn(b"ONS email address", response.data)
        self.assertIn(b"admin password", response.data)
        self.assertEqual(response.status_code, 200)

    # Uncomment once my-account page is enabled in future PR
    @requests_mock.mock()
    def test_my_account_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_get_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/account/my-account", follow_redirects=True)

        self.assertIn(b"Email address:", response.data)
        self.assertIn(b"ons@ons.fake", response.data)
        self.assertIn(b"Username:", response.data)
        self.assertIn(b"uaa_user", response.data)
        self.assertIn(b"Name:", response.data)
        self.assertIn(b"ONS User", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_no_selection_made(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_get_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("account/my-account", data=None, follow_redirects=True)
        self.assertIn(b"You need to choose and option", response.data)

    @requests_mock.mock()
    def test_change_account_name_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_get_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/account/change-account-name", follow_redirects=True)
        self.assertIn(b"First name", response.data)
        self.assertIn(b"ONS", response.data)
        self.assertIn(b"Last name", response.data)
        self.assertIn(b"User", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_change_name(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_get_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_update_name, status_code=200)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": "ONSYES", "last_name": "Userno"},
            )
            self.assertIn(b"Your name has been changed", response.data)

    @requests_mock.mock()
    def test_name_is_empty(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_get_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_update_name, status_code=200)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": "", "last_name": ""},
            )
            self.assertIn(b"First name is required", response.data)
            self.assertIn(b"Last name is required", response.data)

    @requests_mock.mock()
    def test_request_account(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/request-new-account",
                follow_redirects=True,
                data={"email_address": test_email, "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD},
            )
            self.assertIn(b"We have sent an email to fake@ons.gov.uk", response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_account_fails(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=403)
        response = self.client.post(
            "/account/request-new-account",
            follow_redirects=True,
            data={"email_address": test_email, "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD},
        )
        self.assertIn(b"problem trying to send you an email to create an account.", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_account_already_exists(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 1}, status_code=200)
        response = self.client.post(
            "/account/request-new-account",
            follow_redirects=True,
            data={"email_address": test_email, "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD},
        )
        self.assertIn(b"An account already exists for the email fake@ons.gov.uk", response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_account_page(self):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            response = self.client.get(f"/account/create-account/{token}")
            self.assertIn(b"Consider using your ONS username", response.data)
            self.assertIn(b"at least one capital letter", response.data)
            self.assertEqual(response.status_code, 200)

    def test_create_account_page_dodgy_token(self):
        response = self.client.get("/account/create-account/dodgy-token")
        self.assertIn(b"Your link has expired", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_account(self, mock_request):
        with self.app.app_context():
            with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
                mock_notify()._send_message.return_value = mock.Mock()
                token = token_decoder.generate_email_token(test_email)
                mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
                mock_request.post(url_uaa_create_account, json={}, status_code=201)
                response = self.client.post(
                    f"/account/create-account/{token}",
                    follow_redirects=True,
                    data={
                        "password": "TestPassword1!",
                        "password_confirm": "TestPassword1!",
                        "user_name": "testname",
                        "first_name": "Test",
                        "last_name": "Account",
                    },
                )
                self.assertIn(b"Account successfully created", response.data)
                self.assertIn(b"Sign in", response.data)
                self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_account_different_passwords(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            response = self.client.post(
                f"/account/create-account/{token}",
                follow_redirects=True,
                data={
                    "password": "TestPassword1!",
                    "password_confirm": "WrongPassword!",
                    "user_name": "testname",
                    "first_name": "Test",
                    "last_name": "Account",
                },
            )
            self.assertIn(b"Your passwords do not match", response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_account_fails(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.post(url_uaa_create_account, json={}, status_code=403)
            response = self.client.post(
                f"/account/create-account/{token}",
                follow_redirects=True,
                data={
                    "password": "TestPassword1!",
                    "password_confirm": "TestPassword1!",
                    "user_name": "testname",
                    "first_name": "Test",
                    "last_name": "Account",
                },
            )
            self.assertIn(b"problem trying to create your account.", response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_account_username_taken(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.post(url_uaa_create_account, json={}, status_code=409)
            response = self.client.post(
                f"/account/create-account/{token}",
                follow_redirects=True,
                data={
                    "password": "TestPassword1!",
                    "password_confirm": "TestPassword1!",
                    "user_name": "testname",
                    "first_name": "Test",
                    "last_name": "Account",
                },
            )
            self.assertIn(b"Username already in use; please choose another", response.data)
            self.assertEqual(response.status_code, 200)
