import unittest

import requests_mock

from response_operations_ui import app

url_sign_in_data = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'


class TestSignIn(unittest.TestCase):
    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_sign_in_page(self):
        response = self.app.get('/sign-in')
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)

    def test_logout(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'You\'ve logged out', response.data)

    @requests_mock.mock()
    def test_sign_in(self, mock_request):
        mock_request.post(url_sign_in_data, json={"token": "1234abc"}, status_code=201)

        response = self.app.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("View list of business surveys".encode(), response.data)

    @requests_mock.mock()
    def test_fail_sign_in(self, mock_request):
        mock_request.post(url_sign_in_data, json={"token": "1234abc"}, status_code=500)

        response = self.app.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)
