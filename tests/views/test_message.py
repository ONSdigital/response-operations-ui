import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app

get_message_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
with open('tests/test_data/message/messages.json') as json_data:
    message_list = json.load(json_data)


class TestMessage(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    @requests_mock.mock()
    def test_Home(self, mock_request):
        mock_request.get(get_message_list, json=message_list)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("View messages".encode(), response.data)

    @requests_mock.mock()
    def test_Message_list(self, mock_request):
        mock_request.get(get_message_list, json=message_list)

        response = self.app.get("/messages")
        self.assertEqual(response.status_code, 200)
