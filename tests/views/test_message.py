import json
import unittest
import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers.message_controllers import _get_url, send_message
from response_operations_ui.exceptions.exceptions import InternalError

get_message_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages'
with open('tests/test_data/message/messages.json') as json_data:
    message_list = json.load(json_data)


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config.from_object(TestingConfig)

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
    def test_send_message_created(self, mock_request):
        url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message'
        mock_request.post(url, json=self.json)
        response = self.app.post("/messages/create-message")
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_send_message_fail(self, mock_request):
        with app.app_context():
            app.config['BACKSTAGE_API_URL'] = None
            url = f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message'
            mock_request.post(url, json=self.json)

            with self.assertRaises(InternalError):
                send_message(self.json)

    create_message_url = (
        "/messages/create-message?ru_details="
        "survey%3DBRES%2B2017%26"
        "ru_ref%3D49900000280%26"
        "business%3DBolts%2B%2526%2BRachets%2BLtd%26"
        "to%3DJacky%2BTurner%26"
        "to_uuid%3Df62dfda8-73b0-4e0e-97cf-1b06327a6712%26"
        "to_ru_id%3Dc614e64e-d981-4eba-b016-d9822f09a4fb")

    def test_details_fields_prepopulated(self):
        response = self.app.get(self.create_message_url)

        self.assertIn("BRES 2017".encode(), response.data)
        self.assertIn("49900000280".encode(), response.data)
        self.assertIn("Bolts &amp; Rachets Ltd".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)

    def test_empty_subject_and_body_rejected(self):
        response = self.app.post(self.create_message_url)

        self.assertIn("Please enter a subject".encode(), response.data)
        self.assertIn("Please enter a message".encode(), response.data)

    @requests_mock.mock()
    def test_form_submit_with_valid_data(self, mock_request):
        mock_request.post(f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message', status_code=201)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/messages', json={}, status_code=200)

        with app.app_context():
            message_form = {'body': "TEST BODY",
                            'subject': "TEST SUBJECT"}

            response = self.app.post(self.create_message_url, data=message_form, follow_redirects=True)

            self.assertIn("Message sent.".encode(), response.data)

    @requests_mock.mock()
    def test_form_submitted_with_api_error(self, mock_request):
        mock_request.post(f'{app.config["BACKSTAGE_API_URL"]}/v1/secure-message/send-message', status_code=500)

        with app.app_context():
            message_form = {'body': "TEST BODY",
                            'subject': "TEST SUBJECT"}

            response = self.app.post(self.create_message_url, data=message_form, follow_redirects=True)

            self.assertIn(
                "Message failed to send, something has gone wrong with the website.".encode(),
                response.data)

        self.assertIn("BRES 2017".encode(), response.data)
        self.assertIn("49900000280".encode(), response.data)
        self.assertIn("Bolts &amp; Rachets Ltd".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)
