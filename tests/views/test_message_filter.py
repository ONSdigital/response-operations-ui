import json
import unittest
import requests_mock

from config import TestingConfig
from response_operations_ui import app

url_sign_in_data = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'
get_message_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
with open('tests/test_data/message/messages.json') as json_data:
    message_list = json.load(json_data)


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

    # def test_radio_buttons_post(self):
    #     self.app.get("messages/select-survey")
    #     selected_survey = "BRES"
    #     response = self.app.post("messages/select-survey", selected_survey=selected_survey, follow_redirects=True)
    #
    #     self.assertEqual(200, response.status_code)
    #     self.assertIn("filter".encode(), response.data)

    def test_radio_buttons_post_nothing_selected(self):
        response = self.app.post("messages/select-survey", follow_redirects=True)

        self.assertEqual(400, response.status_code)
        self.assertIn("Bad Request".encode(), response.data)

    # @requests_mock.mock()
    # def test_get_BRICKS_messages(self, mock_request):
    #     mock_request.get(get_message_list)
    #
    #     response = self.app.get("/Bricks")
    #
    #     self.assertEqual(response.status_code, 302)
    #     self.assertIn("Walmart".encode(), response.data)
    #
    # def test_get_messages_no_filtered_messages(self):
    #     response = self.app.get("messages/ASHE", json=message_list)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("No new messages".encode(), response.data)
    #
    # def test_get_messages_survey_does_not_exist(self):
    #     response = self.app.get("messages/this-survey", json=message_list)
    #
    #     self.assertEqual(response.status_code, 500)
    #     self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_get_all_messages(self, mock_request):
        mock_request.get(get_message_list, json=message_list)

        response = self.app.get("/messages")

        self.assertIn("Acme Studios LTD".encode(), response.data)
        self.assertIn("Jordon Dutch".encode(), response.data)
        self.assertIn("Q3 Statistics".encode(),response.data)
        self.assertIn("Walmart".encode(), response.data)
        self.assertIn("Andy Robertson".encode(), response.data)
