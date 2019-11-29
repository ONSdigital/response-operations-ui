import unittest
import jwt
import requests_mock

from response_operations_ui import create_app
from config import TestingConfig

test_email = "fake@ons.gov.uk"
url_uaa_token = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_uaa_get_accounts = f"{TestingConfig.UAA_SERVICE_URL}/Users?filter=email+eq+%22{test_email}%22"


class TestAccounts(unittest.TestCase):

    def setUp(self):
        payload = {'user_id': 'test-id',
                   'aud': 'response_operations'}
        app = create_app('TestingConfig')
        self.access_token = jwt.encode(payload, app.config['UAA_PRIVATE_KEY'], algorithm='RS256')
        self.client = app.test_client()

    def test_request_account_page(self):
        response = self.client.get('/request-new-account')
        self.assertIn(b'ONS email address', response.data)
        self.assertIn(b'admin password', response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_request_account(self, mock_request):
        mock_request.post(url_uaa_token, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_uaa_get_accounts, json={"totalResults": 0}, status_code=200)
        response = self.client.post("/request-new-account", follow_redirects=True,
                                    data={"email_address": test_email,
                                          "password": TestingConfig.CREATE_ACCOUNT_ADMIN_PASSWORD})
        self.assertIn(b'We have sent an email to fake@ons.gov.uk', response.data)
        self.assertEqual(response.status_code, 200)
