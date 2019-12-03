import copy
import json
from unittest.mock import patch

import jwt
import requests_mock

from config import TestingConfig
from response_operations_ui.controllers.message_controllers import get_conversation, send_message
from response_operations_ui.exceptions.exceptions import InternalError
from response_operations_ui.views.messages import _get_to_id, _calculate_page
from response_operations_ui.views.messages import _get_unread_status
from tests.views import ViewTestCase

url_get_party_by_ru_ref = f'{TestingConfig.PARTY_URL}/party-api/v1/parties/type/B/ref/'
shortname_url = f'{TestingConfig.SURVEY_URL}/surveys/shortname'
url_sign_in_data = f'{TestingConfig.UAA_SERVICE_URL}/oauth/token'
url_get_surveys_list = f'{TestingConfig.SURVEY_URL}/surveys/surveytype/Business'
url_get_thread = f'{TestingConfig.SECURE_MESSAGE_URL}/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af'
url_get_threads_list = f'{TestingConfig.SECURE_MESSAGE_URL}/threads'
url_send_message = f'{TestingConfig.SECURE_MESSAGE_URL}/messages'
url_messages = f'{TestingConfig.SECURE_MESSAGE_URL}/messages'
url_update_label = f'{TestingConfig.SECURE_MESSAGE_URL}/messages/modify/ae46748b-c6e6-4859-a57a-86e01db2dcbc'
url_modify_label_base = f'{TestingConfig.SECURE_MESSAGE_URL}/messages/modify/'
url_select_survey = f'{TestingConfig.SECURE_MESSAGE_URL}/messages/select-survey'

survey_id = '6aa8896f-ced5-4694-800c-6cd661b0c8b2'
params = f'?survey={survey_id}&page=1&limit=10'

with open('tests/test_data/message/thread.json') as json_data:
    thread_json = json.load(json_data)

with open('tests/test_data/message/thread_missing_subject.json') as json_data:
    thread_missing_subject = json.load(json_data)

with open('tests/test_data/message/threads.json') as json_data:
    thread_list = json.load(json_data)

with open('tests/test_data/message/threads_multipage.json') as json_data:
    thread_list_multi_page = json.load(json_data)

with open('tests/test_data/message/threads_multipage_multi_ru.json') as json_data:
    thread_list_multi_page_multi_ru = json.load(json_data)

with open('tests/test_data/survey/survey_list.json') as json_data:
    survey_list = json.load(json_data)

with open('tests/test_data/survey/ashe_response.json') as json_data:
    ashe_info = json.load(json_data)

with open('tests/test_data/message/threads_no_unread.json') as json_data:
    threads_no_unread_list = json.load(json_data)

with open('tests/test_data/message/threads_unread.json') as json_data:
    threads_unread_list = json.load(json_data)

with open('tests/test_data/message/thread_unread.json') as json_data:
    thread_unread_json = json.load(json_data)


class TestMessage(ViewTestCase):

    def setup_data(self):
        self.surveys_list_json = [
            {
                "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
                "shortName": "ASHE",
                "longName": "ASHE long name",
                "surveyRef": "123"

            }
        ]
        self.before()

    @requests_mock.mock()
    def before(self, mock_request):
        payload = {'user_id': 'test-id',
                   'aud': 'response_operations'}

        access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm='RS256')
        mock_request.post(url_sign_in_data, json={"access_token": access_token.decode()}, status_code=201)
        # sign-in to setup the user in the session
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

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
        mock_request.get(shortname_url + "/ASHE", status_code=500)

        response = self.client.get("/messages/ASHE", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_atmsg_to(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_atmsg_to.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_atmsg_from(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_atmsg_from.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Deleted respondent".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_msg_to(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_msg_to.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_date(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_sent_date.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_ru_ref(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_ru_ref.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_with_missing_business_name(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/threads_missing_business_name.json') as thread_json:
            malformed_thread_list = json.load(thread_json)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=malformed_thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_fail(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, status_code=500)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_threads_list_empty(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        # If response doesn't have a messages key then it shouldn't give a server error,
        # but instead log the problem and display an empty inbox to the user.

        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json={"messages": []})
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("No new conversations".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation_count_response_error(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=500)

        response = self.client.get("/messages/ASHE", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_read_messages_are_displayed_correctly(self, mock_request):
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=threads_no_unread_list)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

        self.assertNotIn("message-list__item--unread".encode(), response.data)
        self.assertNotIn("circle-icon".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_unread_messages_are_displayed_correctly(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=threads_unread_list)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.get("/messages/ASHE")

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
        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Unread Message Subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_thread_sent_to_GROUP_mark_unread_displayed(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Mark as unread".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_thread_with_deleted_user_cannot_be_replied_to(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with open('tests/test_data/message/thread_missing_respondent.json') as thread_json:
            missing_user_json = json.load(thread_json)
        mock_request.get(url_get_thread, json=missing_user_json)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Cannot reply or modify conversation as the respondent has been deleted".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_thread_sent_to_different_user_mark_unread_not_displayed(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        test_data = copy.deepcopy(thread_unread_json)
        test_data["messages"][0]["msg_to"] = ["SomeoneElse"]
        mock_request.get(url_get_thread, json=test_data)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertNotIn("Mark as unread".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_read_thread_sent_to_same_user_mark_unread_displayed(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        test_data = copy.deepcopy(thread_unread_json)
        test_data["messages"][0]["msg_to"] = ["test-id"]
        mock_request.get(url_get_thread, json=test_data)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Mark as unread".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_thread_when_update_label_fails(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label, status_code=500)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af')

        self.assertIn("Unread Message Subject".encode(), response.data)

    def test_get_conversation_fail_when_no_configuration_key(self):
        with self.app.app_context():
            self.app.config.pop('SECURE_MESSAGE_URL')

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
        mock_request.get(url_get_threads_list, json={})
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong".encode(), response.data)

    @requests_mock.mock()
    def test_send_message_fail(self, mock_request):
        with self.app.app_context():
            self.app.config.pop('SECURE_MESSAGE_URL')
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
                  'business_id': 'c614e64e-d981-4eba-b016-d9822f09a4fb'}

    def test_details_fields_prepopulated(self):
        response = self.client.post("/messages/create-message", data=self.ru_details)

        self.assertIn("BRES 2017".encode(), response.data)
        self.assertIn("49900000280".encode(), response.data)
        self.assertIn("Bolts & Rachets Ltd".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)

    def test_empty_subject_and_body_rejected(self):
        response = self.client.post("/messages/create-message")

        self.assertIn("Please enter a subject".encode(), response.data)
        self.assertIn("Please enter a message".encode(), response.data)

    message_form = {'body': "TEST BODY",
                    'subject': "TEST SUBJECT",
                    'hidden_survey': "ASHE"}
    FDI_message = {'body': "AIFDI BODY",
                   'subject': "AIFDI SUBJECT",
                   'hidden_survey': "AIFDI"}
    AIFDI_response = {
        "id": "41320b22-b425-4fba-a90e-718898f718ce",
        "shortName": "AIFDI",
        "longName": "Annual Inward Foreign Direct Investment Survey",
        "surveyRef": "062",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947"
    }
    AOFDI_response = {
        "id": "04dbb407-4438-4f89-acc4-53445d75330c",
        "shortName": "AOFDI",
        "longName": "Annual Outward Foreign Direct Investment Survey",
        "surveyRef": "063",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947"
    }
    QIFDI_response = {
        "id": "c3eaeff3-d570-475d-9859-32c3bf87800d",
        "shortName": "QIFDI",
        "longName": "Quarterly Inward Foreign Direct Investment Survey",
        "surveyRef": "064",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947"
    }
    QOFDI_response = {
        "id": "57a43c94-9f81-4f33-bad8-f94800a66503",
        "shortName": "QOFDI",
        "longName": "Quarterly Outward Foreign Direct Investment Survey",
        "surveyRef": "065",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947"
    }

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_form_submit_with_valid_data(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.post(url_send_message, json=threads_no_unread_list, status_code=201)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        with self.app.app_context():
            response = self.client.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message sent.".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_form_submit_with_FDI_data(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.post(url_send_message, json=threads_no_unread_list, status_code=201)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)

        # Mocking FDI responses
        mock_request.get(shortname_url + "/QIFDI", json=self.QIFDI_response)
        mock_request.get(shortname_url + "/QOFDI", json=self.QOFDI_response)
        mock_request.get(shortname_url + "/AIFDI", json=self.AIFDI_response)
        mock_request.get(shortname_url + "/AOFDI", json=self.AOFDI_response)

        with self.app.app_context():
            response = self.client.post("/messages/create-message", data=self.FDI_message, follow_redirects=True)

        self.assertIn("Message sent.".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_form_submitted_with_api_error(self, mock_request, mock_get_jwt):
        mock_request.post(url_send_message, status_code=500)
        mock_get_jwt.return_value = "blah"

        with self.app.app_context():
            response = self.client.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message failed to send, something has gone wrong with the website.".encode(), response.data)
        self.assertIn("TEST SUBJECT".encode(), response.data)
        self.assertIn("TEST BODY".encode(), response.data)

    def test_link_post_details_malformed(self):
        malformed_ru_details = {'create-message': 'create-message-view'}
        with self.assertRaises(Exception) as raises:
            self.client.post("/messages/create-message", data=malformed_ru_details)
            self.assertEqual(raises.exception.message, "Failed to load create message page")

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Need more information on project".encode(), response.data)
        self.assertIn("Project ideas".encode(), response.data)
        self.assertIn("49900000001".encode(), response.data)
        self.assertIn("Apple".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation_reply_fail(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af",
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter a message".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation_reply_fail_500(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json, status_code=500)

        response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af",
                                    follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation_reply(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        # Post message on reply
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.post(url_send_message, json=threads_no_unread_list, status_code=201)

        # Conversation list
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)

        response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af",
                                    data=self.message_form,
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("RU Ref".encode(), response.data)
        self.assertIn("Business name".encode(), response.data)
        self.assertIn("Subject".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_conversation_fail(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, status_code=500)

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_conversation_decode_error(self, mock_request):
        mock_request.get(url_get_thread)

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_conversation_key_error(self, mock_request):
        mock_request.get(url_get_thread, json={})

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_radio_buttons(self, mock_request):
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.client.get("/messages/select-survey")

        self.assertEqual(200, response.status_code)
        self.assertIn("Filter messages by survey".encode(), response.data)
        self.assertIn("ASHE".encode(), response.data)
        self.assertIn("Bricks".encode(), response.data)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("FDI".encode(), response.data)

    @requests_mock.mock()
    def test_dropdown_post_nothing_selected(self, mock_request):
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)

        response = self.client.post("/messages/select-survey", follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("Home".encode(), response.data)
        self.assertIn("filter your messages".encode(), response.data)
        self.assertIn("Please select a survey to see messages for your team".encode(), response.data)

    @requests_mock.mock()
    def test_get_messages_survey_does_not_exist(self, mock_request):
        mock_request.get(shortname_url)

        response = self.client.get("/messages/this-survey", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_get_messages_page_without_survey(self, mock_request):
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Filter messages by survey".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_messages_page_with_survey(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        response = self.client.post("/messages/select-survey",
                                    follow_redirects=True,
                                    data={"select-survey": "ASHE"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("ASHE Messages".encode(), response.data)

        response = self.client.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("ASHE Messages".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_messages_page_with_FDI_survey(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=survey_list)

        # Mocking FDI responses
        mock_request.get(shortname_url + "/QIFDI", json=self.QIFDI_response)
        mock_request.get(shortname_url + "/QOFDI", json=self.QOFDI_response)
        mock_request.get(shortname_url + "/AIFDI", json=self.AIFDI_response)
        mock_request.get(shortname_url + "/AOFDI", json=self.AOFDI_response)

        response = self.client.post("/messages/select-survey",
                                    follow_redirects=True,
                                    data={"select-survey": "FDI"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("FDI Messages".encode(), response.data)

        response = self.client.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("FDI Messages".encode(), response.data)

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

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_close_conversation_speedbump(self, mock_request, mock_get_jwt):
        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'QBS'
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation",
                                   follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("Subject".encode(), response.data)
        self.assertIn("Business".encode(), response.data)
        self.assertIn("Reference".encode(), response.data)
        self.assertIn("Respondent".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_close_conversation(self, mock_request, mock_get_jwt):
        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation",
                                    follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("Conversation closed".encode(), response.data)
        self.assertIn("Ashe Messages".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_close_conversation_http_error(self, mock_request, mock_get_jwt):
        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.patch(url_get_thread, json=thread_json, status_code=500)

        response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation",
                                    follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_reopen_conversation(self, mock_request, mock_get_jwt):
        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        with self.app.app_context():
            response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af",
                                        data={'reopen': 'Re-open conversation'},
                                        follow_redirects=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("Conversation re-opened.".encode(), response.data)
        self.assertIn("Ashe Messages".encode(), response.data)

    def test_calculate_page_change(self):
        result = _calculate_page(3, 10, 15)
        self.assertEqual(2, result)

    def test_calculate_page_no_change(self):
        result = _calculate_page(1, 10, 15)
        self.assertEqual(1, result)

    def test_calculate_page_zero_threads(self):
        result = _calculate_page(1, 10, 0)
        self.assertEqual(1, result)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_mark_unread_returns_expected_flash_message(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'QBS'

        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(f"{url_modify_label_base}9ecfad50-2ff5-4bea-a997-d73c4faa73ae")
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get('/messages/mark_unread/9ecfad50-2ff5-4bea-a997-d73c4faa73ae?from=GROUP&to=ONS+User')

        self.assertIn(f"flash_message=Message+from+GROUP+to+ONS+User+marked+unread".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_closeing_conversation_returns_to_correct_tab_and_page(self, mock_request, mock_get_jwt):
        """
            For each tab check that if a conversation is closed then return to the same tab at the same page
        """
        limit = 10
        page = 2
        thread_id = 'fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        mock_request.get(url_messages + '/count', json={"total": limit + 3}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page)

        conversation_tabs = ['my messages', 'open', 'closed', 'initial']
        for conversation_tab in conversation_tabs:
            with self.subTest(conversation_tab=conversation_tab):

                # issue same call as when closing a conversation whilst on page 2 of the selected tab
                url = f"{thread_id}/close-conversation?conversation_tab={conversation_tab}&page={page}&limit={limit}"
                response = self.client.post("/messages/threads/" + url, follow_redirects=True)

                response_body = response.data.decode("utf-8").replace(' ', '')

                self.assertEqual(200, response.status_code)

                # validate that the currently selected tab is as expected (i.e aria-current="location")
                match = f'"/messages/Ashe?conversation_tab={conversation_tab.replace(" ","+")}' \
                    f'&ru_ref_filter=&business_id_filter="aria-current="location"'

                self.assertIn(match, response_body.replace('amp;', ''))

                # and that page 2 is selected
                self.assertIn('<liclass="active"><a>2</a></li>', response_body)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_closeing_conversation_returns_to_previous_tab_if_page_is_now_too_high(self, mock_request, mock_get_jwt):
        """if a conversation is closed then it will dissapear from some tabs. That could mean that the page number
        specified is now too high, this test validates that if that is the case then the previous page is used """

        limit = 10
        page = 4
        thread_id = 'fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        # Returned count is less than 4 pages worth
        mock_request.get(url_messages + '/count', json={"total": (limit * (page - 1)) - 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page)

        conversation_tabs = ['my messages', 'open', 'initial']          # Cant close a thread in the closed tab
        for conversation_tab in conversation_tabs:
            with self.subTest(conversation_tab=conversation_tab):
                # issue same call as when closing a conversation whilst on page 4 of the selected tab
                url = f"{thread_id}/close-conversation?conversation_tab={conversation_tab}&page={page}&limit={limit}"
                response = self.client.post("/messages/threads/" + url, follow_redirects=True)

                response_body = response.data.decode("utf-8").replace(' ', '')

                self.assertEqual(200, response.status_code)

                # validate that the currently selected tab is as expected (i.e aria-current="location")
                match = f'"/messages/Ashe?conversation_tab={conversation_tab.replace(" ","+")}' \
                    f'&ru_ref_filter=&business_id_filter="aria-current="location"'
                self.assertIn(match, response_body.replace('amp;', ''))

                # and that page 3 is selected
                self.assertIn('<liclass="active"><a>3</a></li>', response_body)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_reopening_conversation_returns_to_closed_tab(self, mock_request, mock_get_jwt):
        limit = 10
        page = 4
        thread_id = 'fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        mock_request.get(url_messages + '/count', json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        url = f"/messages/threads/{thread_id}?page={page}&limit={limit}&conversation_tab=closed"
        response = self.client.post(url, data={'reopen': 'Re-open conversation'}, follow_redirects=True)

        response_body = response.data.decode("utf-8").replace(' ', '')

        # validate that the currently selected tab is as expected (i.e aria-current="location")
        match_str = 'aria-current="location"role="menuitem">Closed'
        self.assertIn(match_str, response_body)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def test_filter_threads_limits_by_ru_on_post(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that business_id_filter is passed as a parameter to get count and get messages
        And that the expected call to get by ru_ref from party is called after passing validation
        and that ru_ref_filter and business_id_filter parameters are present
        It is a function of secure message to actually return the correct messages"""
        limit = 15
        page = 1
        business_id_filter = '123'
        ru_ref_filter = '12345678901'
        conversation_tab = 'closed'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        party_get_by_ru_ref = f'{url_get_party_by_ru_ref}{ru_ref_filter}'
        mock_request.get(party_get_by_ru_ref, json={'id': business_id_filter})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}" \
            f"&business_id_filter={business_id_filter}"
        response = self.client.post(url, follow_redirects=True, json={'ru_ref_filter': ru_ref_filter})
        response_body = response.data.decode("utf-8").replace(' ', '')

        self.assertEqual(200, response.status_code)
        mock_get_count.assert_called_with(survey_id=['6aa8896f-ced5-4694-800c-6cd661b0c8b2'],
                                          business_id=business_id_filter,
                                          conversation_tab=conversation_tab)

        query = f'survey={survey_id}&is_closed=true&my_conversations=false&new_respondent_conversations=false&' \
            f'business_id={business_id_filter}&page={page}&limit={limit}'
        assert self._mock_request_called_with_expected_query(mock_request, query)

        assert self._mock_request_called_with_expected_path(mock_request, party_get_by_ru_ref)

        assert 'ru_ref_filter' in response_body
        assert 'business_id' in response_body

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def test_filter_threads_limits_by_ru_on_get(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that business_id_filter is passed as a parameter to get count and get messages
        and that ru_ref_filter and business_id_filter parameters are present
        It is a function of secure message to actually return the correct messages"""
        limit = 15
        page = 1
        business_id_filter = '123'
        conversation_tab = 'closed'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}" \
            f"&business_id_filter={business_id_filter}"
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8").replace(' ', '')

        self.assertEqual(200, response.status_code)
        mock_get_count.assert_called_with(survey_id=['6aa8896f-ced5-4694-800c-6cd661b0c8b2'], 
                                          business_id=business_id_filter,
                                          conversation_tab=conversation_tab)

        query = f'survey={survey_id}&is_closed=true&my_conversations=false&new_respondent_conversations=false&' \
            f'business_id={business_id_filter}&page={page}&limit={limit}'
        assert self._mock_request_called_with_expected_query(mock_request, query)

        assert 'ru_ref_filter' in response_body
        assert 'business_id_filter' in response_body

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def test_filter_threads_clear_filter_displayed_when_filter_active(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that when the filter is in operation the clear filter is displayed"""
        limit = 15
        page = 1
        business_id_filter = '123'
        ru_ref_filter = '12345678901'
        conversation_tab = 'closed'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        party_get_by_ru_ref = f'{url_get_party_by_ru_ref}{ru_ref_filter}'
        mock_request.get(party_get_by_ru_ref, json={'id': business_id_filter})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}" \
            f"&business_id_filter={business_id_filter}"
        response = self.client.post(url, follow_redirects=True, json={'ru_ref_filter': ru_ref_filter})
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert f'Filtered by RU ref: {ru_ref_filter}' in response_body

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def test_filter_threads_no_clear_filter_when_filter_not_active(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that when the filter is cleared via the clear filter link then the
        clear filter link is removed"""
        limit = 15
        page = 1
        business_id_filter = '123'
        ru_ref = '12345678901'
        conversation_tab = 'closed'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        party_get_by_ru_ref = f'{url_get_party_by_ru_ref}{ru_ref}'
        mock_request.get(party_get_by_ru_ref, json={'id': business_id_filter})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # Call clear filter endpoint , passing in ru ref and business id
        url = f"/messages/clear_filter/Ashe?page={page}&limit={limit}&" \
            f"conversation_tab={conversation_tab}&business_id_filter={business_id_filter}&ru_ref={ru_ref}"
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert f'Filtered by RU ref' not in response_body

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def test_filter_threads_display_flash_if_ru_ref_unknown(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that flash message is displayed when ru ref is not known and filter applied"""
        limit = 15
        page = 1
        business_id_filter = '123'
        ru_ref_filter = '12345678901'
        conversation_tab = 'closed'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        party_get_by_ru_ref = f'{url_get_party_by_ru_ref}{ru_ref_filter}'
        mock_request.get(party_get_by_ru_ref, json={'id': ''})  # Party returns no data so flash should display later
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}" \
            f"&business_id_filter={business_id_filter}"
        response = self.client.post(url, follow_redirects=True, json={'ru_ref_filter': ru_ref_filter})
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert f'id="flashed-message-1' in response_body

        assert f'Filter not applied: {ru_ref_filter} is an unknown RU ref' in response_body

    def test_message_no_new_conversations_displayed_on_empty_open_tab(self):
        """Validate that No new conversations displayed on empty open tab"""
        self._validate_no_messages_text('open', 'No new conversations')

    def test_message_no_new_conversations_displayed_on_empty_closed_tab(self):
        """Validate that No closed conversations displayed on empty closed tab"""
        self._validate_no_messages_text('closed', 'No closed conversations')

    def test_message_no_new_conversations_displayed_on_empty_my_conversations_tab(self):
        """Validate that No closed conversations displayed on empty my conversations tab"""
        self._validate_no_messages_text('my messages', 'There are currently no messages')

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def _validate_no_messages_text(self, conversation_tab, expected_text, mock_request, mock_get_count, mock_get_jwt):
        limit = 15
        page = 1
        business_id_filter = '123'
        ru_ref_filter = '12345678901'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"
        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])
        party_get_by_ru_ref = f'{url_get_party_by_ru_ref}{ru_ref_filter}'
        mock_request.get(party_get_by_ru_ref, json={'id': ''})  # Party returns no data so flash should display later
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json={'messages': []})
        mock_get_count.return_value = 0
        # view survey with filter of business_id
        url = f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}" \
            f"&business_id_filter={business_id_filter}&ru_ref={ru_ref_filter}"
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)
        self.assertIn(expected_text, response_body)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    @patch('response_operations_ui.controllers.message_controllers.get_conversation_count')
    def test_messages_tabs_are_displayed(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that the expected tabs are in the returned html"""
        limit = 15
        page = 1
        business_id_filter = '123'
        conversation_tab = 'closed'

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}" \
            f"&business_id_filter={business_id_filter}"
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)
        self.assertIn('href="/messages/Ashe?conversation_tab=my+messages', response_body)
        self.assertIn('href="/messages/Ashe?conversation_tab=open', response_body)
        self.assertIn('href="/messages/Ashe?conversation_tab=closed', response_body)
        self.assertIn('href="/messages/Ashe?conversation_tab=initial', response_body)

    @requests_mock.mock()
    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_messages_survey_dropdown_displayed_on_select_survey_page(self, mock_request, mock_get_jwt):
        """Validate that the survey drop down is in the returned """

        with self.client.session_transaction() as session:
            session['messages_survey_selection'] = 'Ashe'
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info['survey'])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)

        response = self.client.get(url_select_survey, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)
        self.assertIn('id="survey-list"', response_body)

    @staticmethod
    def _mock_request_called_with_expected_query(mock_instance, query):
        for element in mock_instance.request_history:
            if element.query == query:
                return True

        return False

    @staticmethod
    def _mock_request_called_with_expected_path(mock_instance, path):
        for element in mock_instance.request_history:
            if element.path.lower() in path.lower():
                return True

        return False
