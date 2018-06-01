import unittest

import jwt
import requests_mock

from response_operations_ui import app

url_sign_in_data = f'{app.config["UAA_SERVICE_URL"]}/oauth/token'
url_surveys = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/surveys'


class TestSignIn(unittest.TestCase):
    def setUp(self):
        app.config['SECRET_KEY'] = 'sekrit!'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config["UAA_PUBLIC_KEY"] = "Test"

        payload = {'user_id': 'test-id',
                   'aud': 'response_operations'}

        key = app.config["UAA_PUBLIC_KEY"]

        self.access_token = jwt.encode(payload, key=key)
        self.app = app.test_client()

    def test_sign_in_page(self):
        response = self.app.get('/sign-in')
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Sign out", response.data)

    def test_logout(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'You are now signed out', response.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Sign out", response.data)

    @requests_mock.mock()
    def test_sign_in(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token.decode()}, status_code=201)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("View list of business surveys".encode(), response.data)
        self.assertIn("Sign out".encode(), response.data)

    @requests_mock.mock()
    def test_sign_in_unable_to_decode_token(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": 'invalid'}, status_code=201)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error 500 - Server error', response.data)

    @requests_mock.mock()
    def test_fail_authentication(self, mock_request):
        mock_request.post(url_sign_in_data, status_code=401)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "wrong"})

        self.assertEqual(response.status_code, 200)

        self.assertIn(b'Incorrect username or password', response.data)

    @requests_mock.mock()
    def test_fail_authentication_missing_token(self, mock_request):
        mock_request.post(url_sign_in_data, json={}, status_code=201)  # No token in response

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "wrong"})

        self.assertEqual(response.status_code, 200)

        self.assertIn(b'Incorrect username or password', response.data)

    @requests_mock.mock()
    def test_fail_server_error(self, mock_request):
        mock_request.post(url_sign_in_data, status_code=500)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error 500 - Server error', response.data)

    @requests_mock.mock()
    def test_sign_in_redirect_while_authenticated(self, mock_request):
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token.decode()}, status_code=201)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "pass"})

        self.assertIn("View list of business surveys".encode(), response.data)

        # First test that we hit a redirect
        response = self.app.get('/sign-in')
        self.assertEqual(response.status_code, 302)

        # Then test that the redirect takes you to the home page.
        response = self.app.get('/sign-in', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("View list of business surveys".encode(), response.data)

    @requests_mock.mock()
    def test_sign_in_next_url(self, mock_request):
        with self.app.session_transaction() as session:
            session['next'] = '/surveys'
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token.decode()}, status_code=201)
        mock_request.get(url_surveys, json=[{
            "id": "75b19ea0-69a4-4c58-8d7f-4458c8f43f5c",
            "legalBasis": "Statistics of Trade Act 1947",
            "longName": "Monthly Business Survey - Retail Sales Index",
            "shortName": "RSI",
            "surveyRef": "023"}],
            status_code=200)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Surveys".encode(), response.data)
        self.assertIn("Legal basis".encode(), response.data)
        self.assertIn("Statistics of Trade Act 1947".encode(), response.data)

    def test_sign_out_deleting_session_variables(self):
        with self.app.session_transaction() as session:
            session['next'] = '/messages/bricks'
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'You are now signed out', response.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Sign out", response.data)
        with self.app.session_transaction() as session:
            self.assertEqual(session.get("next"), None)
