import unittest

import requests_mock

from response_operations_ui import app

url_sign_in_data = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'
url_surveys = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/surveys'


class TestSignIn(unittest.TestCase):
    def setUp(self):
        app.config['SECRET_KEY'] = 'sekrit!'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_sign_in_page(self):
        response = self.app.get('/sign-in')
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Sign out", response.data)

    def test_logout(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'You\'ve logged out', response.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Sign out", response.data)

    @requests_mock.mock()
    def test_sign_in(self, mock_request):
        mock_request.post(url_sign_in_data, json={"token": "1234abc"}, status_code=201)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("View list of business surveys".encode(), response.data)
        self.assertIn("Sign out".encode(), response.data)

    @requests_mock.mock()
    def test_fail_authentication(self, mock_request):
        mock_request.post(url_sign_in_data, json={"token": "1234abc"}, status_code=401)

        response = self.app.post("/sign-in", follow_redirects=True,
                                 data={"username": "user", "password": "wrong"})

        self.assertEqual(response.status_code, 200)

        # TODO - When RAD have defined what message or error to display on a 401
        # these tests should be expanded to test for the relevant error message
        # being displayed on the page
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)

    @requests_mock.mock()
    def test_sign_in_redirect_while_authenticated(self, mock_request):
        mock_request.post(url_sign_in_data, json={"token": "1234abc"}, status_code=201)

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
        mock_request.post(url_sign_in_data, json={"token": "1234abc"}, status_code=201)
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
