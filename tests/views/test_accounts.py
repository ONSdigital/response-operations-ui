import json
import os
import unittest
from unittest import mock
from unittest.mock import Mock, patch

import jwt
import requests_mock
from flask_wtf.csrf import CSRFProtect

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.common import token_decoder
from response_operations_ui.exceptions.exceptions import NotifyError

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)

test_email = "fake@ons.gov.uk"
user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
max_256_characters = (
    "JZPKbNXWhztnGvFbHwfRlcRnpgFjQveWVqvkVgtVVXjcXwiiVvFCmbFAsBVUnjHoaLAOeNUsBHQIczjzuacJUDzLLwWjhBVyVrMf"
    "rLNZQJQDvEeUFDgatOtwajCPNwskfDiGKSVrwdxKRfwsMiTlnslXANitYMaCWGMdSCprQmEIcMchYZgcBxMWFFgHzEljoNZTWTsd"
    "sCEQiQycWJauMkduKmyzaxKxSZNtYxNpsyVGTxqroIUPwQSwXwyjLkkn"
)
csrftoken = "mytoken-OWY4NmQwODE4ODRjN2Q2NTlhMmZlYWEwYzU1YWQwMTVhM2JmNGYxYjJiMGI4MjJjZDE1ZDZMGYwMGEwOA=="
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_get_accounts = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{test_email}%22"
url_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_uaa_user_password_change = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}/password"
url_uaa_create_account = f"{TestingConfig.UAA_SERVICE_URL}/Users"


# noinspection DuplicatedCode
class TestAccounts(unittest.TestCase):
    # csrftoken = generate_csrf()

    def setUp(self):
        payload = {"user_id": user_id, "aud": "response_operations"}
        self.app = create_app("TestingConfig")
        self.access_token = jwt.encode(payload, self.app.config["UAA_PRIVATE_KEY"], algorithm="RS256")
        self.client = self.app.test_client()
        CSRFProtect(self.app)
        self.app.config["WTF_CSRF_ENABLED"] = True

    def test_request_account_page(self):
        response = self.client.get("/account/request-new-account")
        self.assertIn(b"ONS email address", response.data)
        self.assertIn(b"admin password", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_my_account_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/account/my-account", follow_redirects=True)

        self.assertIn(b"Email address:", response.data)
        self.assertIn(b"ons@ons.fake", response.data)
        self.assertIn(b"Username:", response.data)
        self.assertIn(b"uaa_user", response.data)
        self.assertIn(b"Name:", response.data)
        self.assertIn(b"ONS User", response.data)
        self.assertIn(b"Change username", response.data)
        self.assertIn(b"Change name", response.data)
        self.assertIn(b"Change email address", response.data)
        self.assertIn(b"Change password", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_no_selection_made(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.post("account/my-account", data=None, follow_redirects=True)
        self.assertIn(b"You need to choose an option", response.data)

    @requests_mock.mock()
    def test_change_account_name_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(
            url_uaa_token, json={"access_token": self.access_token, "csrftoken": csrftoken}, status_code=201
        )
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
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
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
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
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": "", "last_name": ""},
            )
            self.assertIn(b"First name is required", response.data)
            self.assertIn(b"Last name is required", response.data)

    @requests_mock.mock()
    def test_name_is_max_name_length(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": max_256_characters, "last_name": max_256_characters},
            )
            self.assertIn(b"Your first name must be less than 255 characters", response.data)
            self.assertIn(b"Your last name must be less than 255 characters", response.data)

    @requests_mock.mock()
    def test_name_notify_failure(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify().request_to_notify.side_effect = Mock(side_effect=NotifyError)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": "ONS", "last_name": "user"},
            )
            self.assertIn(b"Something went wrong while updating your name. Please try again", response.data)

    @requests_mock.mock()
    def test_name_uaa_error(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=403)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": "ONS", "last_name": "user"},
            )
            self.assertIn(
                b"Something went wrong. Please ignore the email you have received and try again", response.data
            )

    @requests_mock.mock()
    def test_change_username_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/account/change-username", follow_redirects=True)
        self.assertIn(b"Username", response.data)
        self.assertIn(b"uaa_user", response.data)  # look into this
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_change_username(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": "uaauser"},
            )
            self.assertIn(b"Your username has been changed", response.data)

    @requests_mock.mock()
    def test_username_is_empty(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": ""},
            )
            self.assertIn(b"Username is required", response.data)

    @requests_mock.mock()
    def test_username_is_max_name_length(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": max_256_characters},
            )
            self.assertIn(b"Username must be less than 255 characters", response.data)

    @requests_mock.mock()
    def test_username_contains_wrong_chars(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": "uaa_user"},
            )
            self.assertIn(b"Username can only contain lowercase letters and numbers", response.data)

    @requests_mock.mock()
    def test_username_max_length_and_wrong_character_errors(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": max_256_characters + "!"},
            )
            self.assertIn(b"Username must be less than 255 characters", response.data)
            self.assertIn(b"Username can only contain lowercase letters and numbers", response.data)

    @requests_mock.mock()
    def test_username_already_exists(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=400)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": "uaauser"},
            )
            self.assertIn(b"Username already in use", response.data)

    @requests_mock.mock()
    def test_change_username_notify_failure(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify().request_to_notify.side_effect = Mock(side_effect=NotifyError)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": "uaauser"},
            )
            self.assertIn(b"Something went wrong while updating your username. Please try again", response.data)

    @requests_mock.mock()
    def test_username_uaa_error(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=403)
            response = self.client.post(
                "/account/change-username",
                follow_redirects=True,
                data={"username": "uaauser"},
            )
            self.assertIn(
                b"Something went wrong. Please ignore the email you have received and try again", response.data
            )

    @requests_mock.mock()
    def test_change_email_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/account/change-email", follow_redirects=True)
        self.assertIn(b"New email address", response.data)
        self.assertIn(b"Re-type new email address", response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_change_email_request(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": "fake@ons.gov.uk", "email_confirm": "fake@ons.gov.uk"},
            )
            self.assertIn(b"A verification email has been sent", response.data)

    @requests_mock.mock()
    def test_email_verification(self, mock_request):
        with self.app.app_context():
            with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
                with self.client.session_transaction() as session:
                    session["user_id"] = user_id
                mock_notify()._send_message.return_value = mock.Mock()
                token = token_decoder.generate_email_token(test_email)
                mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
                mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
                mock_request.put(url_uaa_user_by_id, status_code=200)
                mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
                response = self.client.get(
                    f"/account/verify-email/{token}",
                    follow_redirects=True,
                )
                self.assertIn(b"Your email has been changed", response.data)

    @requests_mock.mock()
    def test_change_email_notify_failure(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify().request_to_notify.side_effect = Mock(side_effect=NotifyError)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": "fake@ons.gov.uk", "email_confirm": "fake@ons.gov.uk"},
            )
            self.assertIn(b"Something went wrong while updating your email. Please try again", response.data)

    @requests_mock.mock()
    def test_change_email_uaa_failure(self, mock_request):
        with self.app.app_context():
            with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
                with self.client.session_transaction() as session:
                    session["user_id"] = user_id
                mock_notify()._send_message.return_value = mock.Mock()
                token = token_decoder.generate_email_token(test_email)
                mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
                mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
                mock_request.put(url_uaa_user_by_id, status_code=403)
                mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
                response = self.client.get(
                    f"/account/verify-email/{token}",
                    follow_redirects=True,
                )
                self.assertIn(b"Failed to update email. Please try again", response.data)

    @requests_mock.mock()
    def test_email_is_empty(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": "", "email_confirm": ""},
            )
            self.assertIn(b"Enter an email address", response.data)

    @requests_mock.mock()
    def test_email_is_max_name_length(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": max_256_characters + "@ons.fake"},
            )
            self.assertIn(b"Invalid email", response.data)
            self.assertIn(b"Your email must be less than 255 characters", response.data)

    @requests_mock.mock()
    def test_different_emails(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": "fake@ons.gov.uk", "email_confirm": "ons@ons.fake"},
            )
            self.assertIn(b"Your emails do not match", response.data)

    @requests_mock.mock()
    def test_wrong_email_domain(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": "test@test.test"},
            )
            self.assertIn(b"Not a valid ONS email address", response.data)

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

    @requests_mock.mock()
    def test_change_password_selection_made(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        data = {"option": "change_password"}
        response = self.client.post("account/my-account", data=data, follow_redirects=True)
        self.assertIn(b"Change password", response.data)
        self.assertIn(b"Enter current password", response.data)
        self.assertIn(b"Your password must have", response.data)
        self.assertIn(b"New Password", response.data)
        self.assertIn(b"Re-type new password", response.data)

    @requests_mock.mock()
    def test_change_password_no_input(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=200)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={},
            )
            self.assertIn(b"There are 2 errors on this page", response.data)
            self.assertIn(b"Your current password is required", response.data)
            self.assertIn(b"Your new password is required", response.data)

    @requests_mock.mock()
    def test_change_password_wrong_input(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=200)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={"new_password": "something", "new_password_confirm": "something_else"},
            )
            self.assertIn(b"There are 2 errors on this page", response.data)
            self.assertIn(b"Your current password is required", response.data)
            self.assertIn(b"Your passwords do not match", response.data)

    @requests_mock.mock()
    def test_change_password_doesn_not_meet_requirement(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=200)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={"password": "something", "new_password": "something", "new_password_confirm": "something"},
            )
            self.assertIn(b"There is 1 error on this page", response.data)
            self.assertIn(b"Your password doesn't meet the requirements", response.data)

    @requests_mock.mock()
    def test_change_password_current_new_password_same(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=200)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={
                    "password": "Something!100",
                    "new_password": "Something!100",
                    "new_password_confirm": "Something!100",
                },
            )
            self.assertIn(b"There is 1 error on this page", response.data)
            self.assertIn(b"Your new password is the same as your old password", response.data)

    @requests_mock.mock()
    def test_change_password_current_password_incorrect(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=401)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={
                    "password": "Something100",
                    "new_password": "Something!100",
                    "new_password_confirm": "Something!100",
                },
            )
            self.assertIn(
                b"your current password is incorrect. Please re-enter a correct current password.",
                response.data,
            )

    @requests_mock.mock()
    def test_change_password_uaa_error(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=403)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={
                    "password": "Something100",
                    "new_password": "Something!100",
                    "new_password_confirm": "Something!100",
                },
            )
            self.assertIn(
                b"Something went wrong while updating your username. Please try again.",
                response.data,
            )

    @requests_mock.mock()
    def test_change_password_worked_but_notify_failed(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify().request_to_notify.side_effect = Mock(side_effect=NotifyError)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=200)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={
                    "password": "Something100",
                    "new_password": "Something!100",
                    "new_password_confirm": "Something!100",
                },
            )
            self.assertIn(b"Your password has been changed", response.data)
            self.assertIn(b"We were unable to send the password change acknowledgement email.", response.data)

    @requests_mock.mock()
    def test_change_password_success(self, mock_request):
        with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
            with self.client.session_transaction() as session:
                session["user_id"] = user_id
            mock_notify()._send_message.return_value = mock.Mock()
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_password_change, status_code=200)
            response = self.client.post(
                "/account/change-password",
                follow_redirects=True,
                data={
                    "password": "Something100",
                    "new_password": "Something!100",
                    "new_password_confirm": "Something!100",
                },
            )
            self.assertIn(b"Your password has been changed", response.data)
            self.assertNotIn(b"We were unable to send the password change acknowledgement email.", response.data)
