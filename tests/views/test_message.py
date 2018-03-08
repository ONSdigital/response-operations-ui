import json
import unittest
import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.message_controllers import _get_url, send_message
from response_operations_ui.exceptions.exceptions import InternalError

url_get_thread = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af'
with open('tests/test_data/message/thread.json') as json_data:
    thread_json = json.load(json_data)
url_sign_in_data = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'
get_message_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
with open('tests/test_data/message/messages.json') as json_data:
    message_list = json.load(json_data)


class TestMessage(unittest.TestCase):

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

    # Test Send message API

    def test_get_url_fail_when_no_configuration_key(self):
        with app.app_context():
            app.config['BACKSTAGE_API_URL'] = None

            with self.assertRaises(KeyError):
                _get_url()

    json = '''
        {
          "msg_from": "BRES",
          "msg_to": ["f62dfda8-73b0-4e0e-97cf-1b06327a6712"],
          "subject": "TEST SUBJECT",
          "body": "TEST MESSAGE",
          "thread_id": "",
          "collection_case": "ACollectionCase",
          "survey": "BRES2017",
          "ru_id": "c614e64e-d981-4eba-b016-d9822f09a4fb"
        }
        '''

    # If response doesn't have a messages key then it shouldn't give a server error,
    # but instead log the problem and display an empty inbox to the user.
    @requests_mock.mock()
    def test_request_response_malformed(self, mock_request):
        url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
        mock_request.get(url, json={})
        response = self.app.get("/messages")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong".encode(), response.data)

    @requests_mock.mock()
    def test_send_message_fail(self, mock_request):
        with app.app_context():
            app.config['BACKSTAGE_API_URL'] = None
            url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message'
            mock_request.post(url)

            with self.assertRaises(InternalError):
                send_message(self.json)

    ru_details = {'create-message': 'create-message-view',
                  'survey': 'BRES 2017',
                  'survey_id': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                  'ru_ref': '49900000280',
                  'business': 'Bolts & Rachets Ltd',
                  'msg_to_name': 'Jacky Turner',
                  'msg_to': 'f62dfda8-73b0-4e0e-97cf-1b06327a6712',
                  'ru_id': 'c614e64e-d981-4eba-b016-d9822f09a4fb'}

    def test_details_fields_prepopulated(self):
        response = self.app.post("/messages/create-message", data=self.ru_details)

        self.assertIn("BRES 2017".encode(), response.data)
        self.assertIn("49900000280".encode(), response.data)
        self.assertIn("Bolts & Rachets Ltd".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)

    def test_empty_subject_and_body_rejected(self):
        response = self.app.post("/messages/create-message")

        self.assertIn("Please enter a subject".encode(), response.data)
        self.assertIn("Please enter a message".encode(), response.data)

    message_form = {'body': "TEST BODY",
                    'subject': "TEST SUBJECT"}

    @requests_mock.mock()
    def test_form_submit_with_valid_data(self, mock_request):
        mock_request.post(f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message', status_code=201)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages', json={}, status_code=200)

        with app.app_context():
            response = self.app.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message sent.".encode(), response.data)
        self.assertIn("Inbox".encode(), response.data)

    @requests_mock.mock()
    def test_form_submitted_with_api_error(self, mock_request):
        mock_request.post(f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message', status_code=500)

        with app.app_context():
            response = self.app.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn(
            "Message failed to send, something has gone wrong with the website.".encode(),
            response.data)
        self.assertIn("TEST SUBJECT".encode(), response.data)
        self.assertIn("TEST BODY".encode(), response.data)

    def test_link_post_details_malformed(self):
        malformed_ru_details = {'create-message': 'create-message-view'}
        with self.assertRaises(Exception) as raises:
            self.app.post("/messages/create-message", data=malformed_ru_details)
            self.assertEqual(raises.exception.message, "Failed to load create message page")

    @requests_mock.mock()
    def test_conversation(self, mock_request):
        mock_request.get(url_get_thread, json=thread_json)

        response = self.app.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Need more information on project".encode(), response.data)
        self.assertIn("Project ideas".encode(), response.data)
        self.assertIn("49900000001".encode(), response.data)
        self.assertIn("Apple".encode(), response.data)

    @requests_mock.mock()
    def test_conversation_fail(self, mock_request):
        mock_request.get(url_get_thread, status_code=500)
        with self.assertRaises(Exception) as raises:

            response = self.app.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(raises.exception.message, "Conversation retrieval failed")

    @requests_mock.mock()
    def test_conversation_decode_error(self, mock_request):
        mock_request.get(url_get_thread)
        with self.assertRaises(Exception) as raises:
            response = self.app.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(raises.exception.message, "the response could not be decoded")

    @requests_mock.mock()
    def test_conversation_key_error(self, mock_request):
        mock_request.get(url_get_thread, json={})
        with self.assertRaises(Exception) as raises:
            response = self.app.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(raises.exception.message, "A key error occurred")
