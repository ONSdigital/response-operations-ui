import json
import unittest
import requests_mock

from config import TestingConfig
from response_operations_ui import app

filtered_url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname'
url_sign_in_data = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'
get_message_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
with open('tests/test_data/message/messages.json') as json_data:
    message_list = json.load(json_data)
with open('tests/test_data/survey/bricks_response.json') as json_data:
    bricks_info = json.load(json_data)
with open('tests/test_data/survey/ashe_response.json') as json_data:
    ashe_info = json.load(json_data)


class TestMessageFilter(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config.from_object(TestingConfig)
        self.before()

    @requests_mock.mock()
    def before(self, mock_request):
        mock_request.post(url_sign_in_data, json={"token": "1234abc", "user_id": "test_user"}, status_code=201)
        # sign-in to setup the user in the session
        self.app.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

    def test_radio_buttons_get(self):
        response = self.app.get("messages/select-survey")

        self.assertEqual(200, response.status_code)
        self.assertIn("Filter messages by survey".encode(), response.data)

    def test_radio_buttons_post_nothing_selected(self):
        response = self.app.post("messages/select-survey", follow_redirects=True)

        self.assertEqual(400, response.status_code)
        self.assertIn("Bad Request".encode(), response.data)

    @requests_mock.mock()
    def test_get_bricks_messages(self, mock_request):
        mock_request.get(get_message_list, json=message_list)
        mock_request.get(filtered_url + "/Bricks", json=bricks_info)

        response = self.app.get("/messages/Bricks")

        self.assertEqual(200, response.status_code)
        self.assertIn("Select survey".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)
        self.assertIn("Walmart".encode(), response.data)

    @requests_mock.mock()
    def test_get_ashe_no_messages(self, mock_request):
        mock_request.get(get_message_list, json=message_list)
        mock_request.get(filtered_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE", follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("Select survey".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)
        self.assertIn("No new messages".encode(), response.data)

    @requests_mock.mock()
    def test_get_messages_survey_does_not_exist(self, mock_request):
        mock_request.get(filtered_url)

        response = self.app.get("/messages/this-survey", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_get_all_messages(self, mock_request):
        mock_request.get(get_message_list, json=message_list)

        response = self.app.get("/messages")

        self.assertIn("Acme Studios LTD".encode(), response.data)
        self.assertIn("Jordon Dutch".encode(), response.data)
        self.assertIn("Q3 Statistics".encode(), response.data)
        self.assertIn("Walmart".encode(), response.data)
        self.assertIn("Andy Robertson".encode(), response.data)
