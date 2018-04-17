import json
from unittest.mock import patch
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.views.messages import _get_to_id
from response_operations_ui.controllers.message_controllers import get_conversation, send_message
from response_operations_ui.exceptions.exceptions import InternalError
from response_operations_ui.views.messages import _get_unread_status

shortname_url = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname'
url_sign_in_data = f'{app.config["BACKSTAGE_API_URL"]}/v2/sign-in/'
url_get_surveys_list = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/surveys'
url_get_thread = f'{app.config["SECURE_MESSAGE_URL"]}/v2/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af'
url_get_threads_list = f'{app.config["SECURE_MESSAGE_URL"]}/threads'
url_send_message = f'{app.config["SECURE_MESSAGE_URL"]}/v2/messages'
url_update_label = f'{app.config["SECURE_MESSAGE_URL"]}/v2/messages/modify/ae46748b-c6e6-4859-a57a-86e01db2dcbc'

with open('tests/test_data/message/thread.json') as json_data:
    thread_json = json.load(json_data)

with open('tests/test_data/message/thread_missing_subject.json') as json_data:
    thread_missing_subject = json.load(json_data)

with open('tests/test_data/message/threads.json') as json_data:
    thread_list = json.load(json_data)

with open('tests/test_data/survey/survey_list.json') as json_data:
    survey_list = json.load(json_data)

with open('tests/test_data/survey/ashe_response.json') as json_data:
    ashe_info = json.load(json_data)


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

    surveys_list_json = [
        {
            "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
            "shortName": "ASHE",
            "longName": "ASHE long name",
            "surveyRef": "123"

        }
    ]

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Apple".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)
        self.assertIn("John Example".encode(), response.data)
        self.assertIn("ASHE Team".encode(), response.data)
        self.assertIn("Message from respondent".encode(), response.data)
        self.assertIn("Message from ONS".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_survey_short_name_failure(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", status_code=500)

        response = self.app.get("/messages/ASHE", follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Something has gone wrong with the website.".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_atmsg_to(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_atmsg_to.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_atmsg_from(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_atmsg_from.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_msg_to(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_msg_to.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_date(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_sent_date.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_ru_ref(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_ru_ref.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_business_name(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_business_name.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    def test_threads_list_fail(self, mock_request):
        mock_request.get(url_get_threads_list, status_code=500)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_empty(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        # If response doesn't have a messages key then it shouldn't give a server error,
        # but instead log the problem and display an empty inbox to the user.

        mock_request.get(url_get_threads_list, json={"messages": []})
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("No new messages".encode(), response.data)

    @requests_mock.mock()
    def test_read_messages_are_displayed_correctly(self, mock_request):
        with open('tests/test_data/message/threads_no_unread.json') as threads_json:
            threads_no_unread_list = json.load(threads_json)

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=threads_no_unread_list)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertNotIn("message-list__item--unread".encode(), response.data)
        self.assertNotIn("circle-icon".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_unread_messages_are_displayed_correctly(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_unread.json') as threads_json:
            threads_unread_list = json.load(threads_json)

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        params = "?survey=6aa8896f-ced5-4694-800c-6cd661b0c8b2&limit=1000"
        mock_request.get(url_get_threads_list + params, json=threads_unread_list)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        response = self.app.get("/messages/ASHE")
        self.assertIn('name="message-unread"'.encode(), response.data)
        self.assertIn("message-list__item--unread".encode(), response.data)
        self.assertIn("circle-icon".encode(), response.data)

    def test_get_message_unread_status(self):
        unread_message = {"labels": ["INBOX", "UNREAD"]}
        self.assertTrue(_get_unread_status(unread_message))

        read_message = {"labels": ["INBOX"]}
        self.assertFalse(_get_unread_status(read_message))

        message_missing_labels = {}
        self.assertFalse(_get_unread_status(message_missing_labels))

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_thread(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/thread_unread.json') as thread_unread_json:
            thread_unread_json = json.load(thread_unread_json)

        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.app.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Unread Message Subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_thread_when_update_label_fails(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        # The page should still load if the update label call fails
        with open('tests/test_data/message/thread_unread.json') as thread_unread_json:
            thread_unread_json = json.load(thread_unread_json)

        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label, status_code=500)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.app.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Unread Message Subject".encode(), response.data)

    def test_get_conversation_fail_when_no_configuration_key(self):
        with app.app_context():
            app.config.pop('SECURE_MESSAGE_URL')

            with self.assertRaises(KeyError):
                get_conversation("test123")

    message_json = '''
        {
          "msg_from": "BRES",
          "msg_to": ["f62dfda8-73b0-4e0e-97cf-1b06327a6712"],
          "subject": "TEST SUBJECT",
          "body": "TEST MESSAGE",
          "thread_id": "",
          "collection_case": "",
          "survey": "BRES2017",
          "ru_id": "c614e64e-d981-4eba-b016-d9822f09a4fb"
        }
        '''

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_request_response_malformed(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        url = url_get_threads_list
        mock_request.get(url, json={})
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)
        response = self.app.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong".encode(), response.data)

    @requests_mock.mock()
    def test_send_message_fail(self, mock_request):
        with app.app_context():
            app.config.pop('SECURE_MESSAGE_URL')
            url = url_send_message
            mock_request.post(url)

            with self.assertRaises(InternalError):
                send_message(self.message_json)

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
                    'subject': "TEST SUBJECT",
                    'hidden_survey': "ASHE"}

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_form_submit_with_valid_data(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.post(url_send_message, status_code=201)
        mock_request.get(url_get_threads_list, json=thread_list, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        with app.app_context():
            response = self.app.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message sent.".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_form_submitted_with_api_error(self, mock_request, mock_get_jwt):
        mock_request.post(url_send_message, status_code=500)
        mock_get_jwt.return_value = "blah"

        with app.app_context():
            response = self.app.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message failed to send, something has gone wrong with the website.".encode(), response.data)
        self.assertIn("TEST SUBJECT".encode(), response.data)
        self.assertIn("TEST BODY".encode(), response.data)

    def test_link_post_details_malformed(self):
        malformed_ru_details = {'create-message': 'create-message-view'}
        with self.assertRaises(Exception) as raises:
            self.app.post("/messages/create-message", data=malformed_ru_details)
            self.assertEqual(raises.exception.message, "Failed to load create message page")

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.app.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Need more information on project".encode(), response.data)
        self.assertIn("Project ideas".encode(), response.data)
        self.assertIn("49900000001".encode(), response.data)
        self.assertIn("Apple".encode(), response.data)

    @requests_mock.mock()
    def test_conversation_fail(self, mock_request):
        mock_request.get(url_get_thread, status_code=500)
        mock_request.get(url_get_surveys_list, json=survey_list)
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

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation_subject_error(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_missing_subject)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.app.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
        self.assertEqual(response.status_code, 200)
        self.assertIn("No Subject".encode(), response.data)

    def test_get_radio_buttons(self):
        response = self.app.get("/messages/select-survey")

        self.assertEqual(200, response.status_code)
        self.assertIn("Filter messages by survey".encode(), response.data)
        self.assertIn("ASHE".encode(), response.data)
        self.assertIn("Bricks".encode(), response.data)

    @requests_mock.mock()
    def test_radio_buttons_post_nothing_selected(self, mock_request):
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)

        response = self.app.post("/messages/select-survey", follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("Home".encode(), response.data)
        self.assertIn("Please select a survey to filter your messages.".encode(), response.data)
        self.assertIn("Filter messages by survey".encode(), response.data)

    @requests_mock.mock()
    def test_get_messages_survey_does_not_exist(self, mock_request):
        mock_request.get(shortname_url)

        response = self.app.get("/messages/this-survey", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    def test_get_messages_page_without_survey(self):
        response = self.app.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Filter messages by survey".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_messages_page_with_survey(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info)

        posts_survey = {"radio-answer": "ASHE"}

        response = self.app.post("/messages/select-survey", follow_redirects=True, data=posts_survey)

        self.assertEqual(response.status_code, 200)
        self.assertIn("ASHE Messages".encode(), response.data)

        response = self.app.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("ASHE Messages".encode(), response.data)

    def test_get_to_id(self):
        with open('tests/test_data/message/threads.json') as fp:
            conversation = json.load(fp)
        self.assertEqual(conversation['messages'][0]['msg_to'][0],
                         _get_to_id(conversation['messages'][0]))

    def test_get_to_id_index_error(self):
        with open('tests/test_data/message/threads.json') as fp:
            conversation = json.load(fp)
        del conversation['messages'][0]['msg_to'][0]
        self.assertEqual(None, _get_to_id(conversation['messages'][0]))
