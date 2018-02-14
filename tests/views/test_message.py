import json
import unittest

import requests_mock

from response_operations_ui import app

get_message_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
with open('tests/test_data/message/messages.json') as json_data:
    message_list = json.load(json_data)


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @requests_mock.mock()
    def test_Home(self, mock_request):
        mock_request.get(get_message_list, json=message_list)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("View messages".encode(), response.data)

    # Test showing that the messages list loads into the website and displays User, business name and subject
    @requests_mock.mock()
    def test_Message_list(self, mock_request):
        mock_request.get(get_message_list, json=message_list)

        response = self.app.get("/messages")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Acme Studios LTD".encode(), response.data)
        self.assertIn("Jordon Dutch".encode(), response.data)
        self.assertIn("Q3 Statistics".encode(), response.data)

    @requests_mock.mock()
    def test_message_list_fail(self, mock_request):
        mock_request.get(get_message_list, status_code=500)

        response = self.app.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_message_list_empty(self, mock_request):
        mock_request.get(get_message_list, json={"messages": []})

        response = self.app.get("/messages")

        self.assertEqual(response.status_code, 200)
        self.assertIn("No new messages".encode(), response.data)

    # If response doesn't have a messages key then it shouldn't give a server error,
    # but instead log the problem and display an empty inbox to the user.
    @requests_mock.mock()
    def test_request_response_malformed(self, mock_request):
        mock_request.get(get_message_list, json={})
        response = self.app.get("/messages")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong".encode(), response.data)
