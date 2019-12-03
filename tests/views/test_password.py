import unittest
import jwt
import requests_mock

from response_operations_ui import create_app
from config import TestingConfig
from response_operations_ui.common import token_decoder

test_email = "fake@ons.gov.uk"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_get_accounts = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{test_email}%22"
url_uaa_reset_code = f"{TestingConfig.UAA_SERVICE_URL}/password_resets"
url_uaa_reset_pw = f"{TestingConfig.UAA_SERVICE_URL}/password_change"
url_send_req_notify = f'{TestingConfig().NOTIFY_SERVICE_URL}{TestingConfig().NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}'
url_send_cre_notify = f'{TestingConfig().NOTIFY_SERVICE_URL}{TestingConfig().NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}'


class TestPasswords(unittest.TestCase):

    def setUp(self):
        payload = {'user_id': 'test-id',
                   'aud': 'response_operations'}
        self.app = create_app('TestingConfig')
        self.access_token = jwt.encode(payload, self.app.config['UAA_PRIVATE_KEY'], algorithm='RS256')
        self.client = self.app.test_client()

    def test_request_reset_page(self):
        response = self.client.get('/passwords/forgot-password')
        self.assertIn(b'Enter your email address', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_reset(self, mock_request):
        mock_request.post(url_send_req_notify, json={'emailAddress': test_email}, status_code=201)
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts,
                         json={"totalResults": 1,
                               "resources": [{"name": {"givenName": "Test"}}]}, status_code=200)
        response = self.client.post("/passwords/forgot-password", follow_redirects=True,
                                    data={"email_address": test_email})
        self.assertIn(b'If fake@ons.gov.uk is registered to an account', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_reset_fails(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 1}, status_code=403)
        response = self.client.post("/passwords/forgot-password", follow_redirects=True,
                                    data={"email_address": test_email})
        self.assertIn(b'problem trying to send you a password reset email', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_reset_doesnt_exist(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
        response = self.client.post("/passwords/forgot-password", follow_redirects=True,
                                    data={"email_address": test_email})
        self.assertIn(b'If fake@ons.gov.uk is registered to an account', response.data)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page(self):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            response = self.client.get(f'/passwords/reset-password/{token}')
            self.assertIn(b'New password', response.data)
            self.assertIn(b'at least one capital letter', response.data)
            self.assertEqual(response.status_code, 200)

    def test_reset_password_page_dodgy_token(self):
        response = self.client.get(f'/passwords/reset-password/dodgy-token')
        self.assertIn(b'Your link has expired', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_reset_password(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            mock_request.post(url_send_cre_notify, json={'emailAddress': test_email}, status_code=201)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
            mock_request.post(url_uaa_reset_code, json={"code": "testcode"}, status_code=201)
            mock_request.post(url_uaa_reset_pw, status_code=200)
            mock_request.get(url_uaa_get_accounts,
                             json={"totalResults": 1,
                                   "resources": [{"userName": "testuser"}], status_code=200)
            response = self.client.post(f"/passwords/reset-password/{token}", follow_redirects=True,
                                        data={"password": 'TestPassword1!',
                                              "password_confirm": 'TestPassword1!'})
            self.assertIn(b'Your password has been changed', response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_reset_password_different_passwords(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            response = self.client.post(f"/passwords/reset-password/{token}", follow_redirects=True,
                                        data={"password": 'TestPassword1!',
                                              "password_confirm": 'WrongPassword!'})
            self.assertIn(b'Your passwords do not match', response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_reset_password_fails(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
            mock_request.post(url_uaa_reset_code, json={"code": "testcode"}, status_code=201)
            mock_request.post(url_uaa_reset_pw, json={}, status_code=403)
            mock_request.get(url_uaa_get_accounts,
                             json={"totalResults": 1,
                                   "resources": [{"userName": "testuser"}], status_code=200)
            response = self.client.post(f"/passwords/reset-password/{token}", follow_redirects=True,
                                        data={"password": 'TestPassword1!',
                                              "password_confirm": 'TestPassword1!'})
            self.assertIn(b'problem trying to reset your password.', response.data)
            self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_reset_password_old_password(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
            mock_request.post(url_uaa_reset_code, json={"code": "testcode"}, status_code=201)
            mock_request.post(url_uaa_reset_pw, json={}, status_code=422)
            mock_request.get(url_uaa_get_accounts,
                             json={"totalResults": 1,
                                   "resources": [{"userName": "testuser"}], status_code=200)
            response = self.client.post(f"/passwords/reset-password/{token}", follow_redirects=True,
                                        data={"password": 'TestPassword1!',
                                              "password_confirm": 'TestPassword1!'})
            self.assertIn(b'Please choose a different password or login with the old password', response.data)
            self.assertEqual(response.status_code, 200)
