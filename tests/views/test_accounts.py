import json
import os
import unittest
from unittest import mock
from unittest.mock import Mock, patch

import jwt
import requests_mock

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.common import token_decoder
from response_operations_ui.exceptions.exceptions import NotifyError

project_root = os.path.dirname(os.path.dirname(__file__))
with open(f"{project_root}/test_data/uaa/user_by_id.json") as json_data:
    uaa_user_by_id_json = json.load(json_data)

user_id = "fe2dc842-b3b3-4647-8317-858dab82ab94"
user_email = user_id
new_user_email = "new.one@ons.gov.uk"
max_256_characters = (
    "JZPKbNXWhztnGvFbHwfRlcRnpgFjQveWVqvkVgtVVXjcXwiiVvFCmbFAsBVUnjHoaLAOeNUsBHQIczjzuacJUDzLLwWjhBVyVrMf"
    "rLNZQJQDvEeUFDgatOtwajCPNwskfDiGKSVrwdxKRfwsMiTlnslXANitYMaCWGMdSCprQmEIcMchYZgcBxMWFFgHzEljoNZTWTsd"
    "sCEQiQycWJauMkduKmyzaxKxSZNtYxNpsyVGTxqroIUPwQSwXwyjLkkn"
)
csrf_token = "ImRjMmJkZWRhNDcwMDBmM2JlZWEwYWM2YzhkYzMxMzliMjBmYmU1ZWIi.Yhy3Hw.cLsrWJHAXXmBJjLY0J8XP3oE8qw"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_get_accounts = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{user_email}%22"
url_uaa_get_accounts_new_email = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{new_user_email}%22"
url_uaa_user_by_id = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}"
url_uaa_user_password_change = f"{TestingConfig.UAA_SERVICE_URL}/Users/{user_id}/password"
url_uaa_create_account = f"{TestingConfig.UAA_SERVICE_URL}/Users"
url_uaa_password_reset_code = f"{TestingConfig.UAA_SERVICE_URL}/password_resets"
url_uaa_password_change = f"{TestingConfig.UAA_SERVICE_URL}/password_change"


class TestAccounts(unittest.TestCase):
    def setUp(self):
        payload = {"user_id": user_id, "aud": "response_operations"}
        self.app = create_app("TestingConfig")
        self.access_token = jwt.encode(payload, self.app.config["UAA_PRIVATE_KEY"], algorithm="RS256")
        self.client = self.app.test_client()

    @requests_mock.mock()
    def test_my_account_page(self, mock_request):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
        mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
        response = self.client.get("/account/my-account", follow_redirects=True)

        self.assertIn(b"Email address:", response.data)
        self.assertIn(b"some.one@ons.gov.uk", response.data)
        self.assertIn(b"Username:", response.data)
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
        mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
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
            mock_request.post(
                url_uaa_token, json={"access_token": self.access_token, "csrf_token": csrf_token}, status_code=201
            )
            # mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.put(url_uaa_user_by_id, status_code=200)
            response = self.client.post(
                "/account/change-account-name",
                follow_redirects=True,
                data={"first_name": "ONSYES", "last_name": "Userno", "csrf_token": csrf_token},
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
        self.assertIn(b"some.one@ons.gov.uk", response.data)  # look into this
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
                data={"username": "uaa.@_user123"},
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
                data={"username": "uaa_user!"},
            )
            self.assertIn(
                b"Username can only contain lowercase letters, numbers, and special characters (`.`, `@`, and `_`)",
                response.data,
            )

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
            self.assertIn(
                b"Username can only contain lowercase letters, numbers, and special characters (`.`, `@`, and `_`)",
                response.data,
            )

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
            mock_request.get(url_uaa_get_accounts_new_email, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": new_user_email, "email_confirm": new_user_email},
            )
            self.assertIn(b"A verification email has been sent", response.data)

    @requests_mock.mock()
    def test_email_verification(self, mock_request):
        with self.app.app_context():
            with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
                with self.client.session_transaction() as session:
                    session["user_id"] = user_id
                mock_notify()._send_message.return_value = mock.Mock()
                token_dict = {"email": user_email, "user_id": user_id}
                token = token_decoder.generate_token(json.dumps(token_dict))
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
            mock_request.get(url_uaa_get_accounts_new_email, json={"totalResults": 0}, status_code=200)
            response = self.client.post(
                "/account/change-email",
                follow_redirects=True,
                data={"email_address": new_user_email, "email_confirm": new_user_email},
            )
            self.assertIn(b"Something went wrong while updating your email. Please try again", response.data)

    @requests_mock.mock()
    def test_change_email_uaa_failure(self, mock_request):
        with self.app.app_context():
            with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
                with self.client.session_transaction() as session:
                    session["user_id"] = user_id
                mock_notify()._send_message.return_value = mock.Mock()
                token_dict = {"email": user_email, "user_id": user_id}
                token = token_decoder.generate_token(json.dumps(token_dict))
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

    # activate-account

    @requests_mock.mock()
    def test_get_activate_account(self, mock_request):
        with self.app.app_context():
            with patch("response_operations_ui.views.accounts.NotifyController") as mock_notify:
                mock_notify()._send_message.return_value = mock.Mock()
                token = token_decoder.generate_token(user_id)
                mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
                mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
                response = self.client.get(
                    f"/account/activate-account/{token}",
                    follow_redirects=True,
                )
                self.assertIn(b"Activate your account", response.data)
                self.assertIn(b"Activate account", response.data)
                self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_post_activate_account(self, mock_request):
        with self.app.app_context():
            password_reset_code_json = {"code": "f-Ni-kNixp", "user_id": user_id}
            token = token_decoder.generate_token(user_id)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.post(url_uaa_password_reset_code, json=password_reset_code_json, status_code=201)
            mock_request.post(url_uaa_password_change, status_code=200)
            response = self.client.post(
                f"/account/activate-account/{token}",
                follow_redirects=True,
                data={
                    "password": "TestPassword1!",
                    "password_confirm": "TestPassword1!",
                },
            )
            self.assertIn(b"Account successfully activated", response.data)
            self.assertIn(b"Sign in", response.data)
            self.assertIn(b"Forgot password?", response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_post_activate_account_failure(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_token(user_id)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token}, status_code=201)
            mock_request.get(url_uaa_user_by_id, json=uaa_user_by_id_json, status_code=200)
            mock_request.post(url_uaa_password_reset_code, status_code=500)
            response = self.client.post(
                f"/account/activate-account/{token}",
                follow_redirects=True,
                data={
                    "password": "TestPassword1!",
                    "password_confirm": "TestPassword1!",
                },
            )
            self.assertIn(b"Activate your account", response.data)
            self.assertIn(
                b"Something went wrong setting password and activating account, please try again", response.data
            )
            self.assertIn(b"Activate account", response.data)
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
                b"Something went wrong while updating your password. Please try again.",
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
