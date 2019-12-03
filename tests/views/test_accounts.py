import unittest
import jwt
import requests_mock

from response_operations_ui import create_app
from config import TestingConfig
from response_operations_ui.common import token_decoder

test_email = "fake@ons.gov.uk"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_get_accounts = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{test_email}%22"
url_uaa_create_account = f"{TestingConfig.UAA_SERVICE_URL}/Users"
url_send_req_notify = f'{TestingConfig().NOTIFY_SERVICE_URL}{TestingConfig().NOTIFY_REQUEST_CREATE_ACCOUNT_TEMPLATE}'
url_send_cre_notify = f'{TestingConfig().NOTIFY_SERVICE_URL}{TestingConfig().NOTIFY_CONFIRM_CREATE_ACCOUNT_TEMPLATE}'


class TestAccounts(unittest.TestCase):

    def setUp(self):
        payload = {'user_id': 'test-id',
                   'aud': 'response_operations'}
        self.app = create_app('TestingConfig')
        self.access_token = jwt.encode(payload, self.app.config['UAA_PRIVATE_KEY'], algorithm='RS256')
        self.client = self.app.test_client()

    def test_request_account_page(self):
        response = self.client.get('/account/request-new-account')
        self.assertIn(b'ONS email address', response.data)
        self.assertIn(b'admin password', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_account(self, mock_request):
        mock_request.post(url_send_req_notify, json={'emailAddress': test_email}, status_code=201)
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
        response = self.client.post("/account/request-new-account", follow_redirects=True,
                                    data={"email_address": test_email,
                                          "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD})
        self.assertIn(b'We have sent an email to fake@ons.gov.uk', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_account_fails(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=403)
        response = self.client.post("/account/request-new-account", follow_redirects=True,
                                    data={"email_address": test_email,
                                          "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD})
        self.assertIn(b'problem trying to send you a password reset email', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_account_already_exists(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 1}, status_code=200)
        response = self.client.post("/account/request-new-account", follow_redirects=True,
                                    data={"email_address": test_email,
                                          "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD})
        self.assertIn(b'An account already exists for the email fake@ons.gov.uk', response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_account_page(self):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            response = self.client.get(f'/account/create-account/{token}')
            self.assertIn(b'Consider using your ONS username', response.data)
            self.assertIn(b'at least one capital letter', response.data)
            self.assertEqual(response.status_code, 200)

    def test_create_account_page_dodgy_token(self):
        response = self.client.get(f'/account/create-account/dodgy-token')
        self.assertIn(b'Your link has expired', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_account(self, mock_request):
        with self.app.app_context():
            token = token_decoder.generate_email_token(test_email)
            mock_request.post(url_send_cre_notify, json={'emailAddress': test_email}, status_code=201)
            mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
            mock_request.post(url_uaa_create_account, json={}, status_code=201)
            response = self.client.post(f"/account/create-account/{token}", follow_redirects=True,
                                        data={"password": 'TestPassword1!',
                                              "password_confirm": 'TestPassword1!',
                                              "user_name": 'testname',
                                              "first_name": 'Test',
                                              "last_name": 'Account'})
            self.assertIn(b'Account successfully created', response.data)
            self.assertIn(b'Sign in', response.data)
            self.assertEqual(response.status_code, 200)
