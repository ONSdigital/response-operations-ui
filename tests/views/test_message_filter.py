import json
import unittest
import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.message_controllers import _get_url, send_message
from response_operations_ui.exceptions.exceptions import InternalError

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
    def before(self, mock_request=None):
        mock_request.post(url_sign_in_data, json={"token": "1234abc", "user_id": "test_user"}, status_code=201)
        # sign-in to setup the user in the session
        self.app.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

    # basic test ideas

    @requests_mock.mock()
    def test_radio_buttons_get(self, mock_request):
        pass

    @requests_mock.mock()
    def test_radio_buttons_post(self, mock_request):
        pass

    @requests_mock.mock()
    def test_get_BRES_messages(self, mock_request):
        pass

    @requests_mock.mock()
    def test_get_QBS_messages(self, mock_request):
        pass

    @requests_mock.mock()
    def test_get_all_messages(self, mock_request):
        pass
