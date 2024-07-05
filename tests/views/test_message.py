import copy
import json
import os
from unittest.mock import patch

import fakeredis
import jwt
import requests_mock

from config import TestingConfig
from response_operations_ui.controllers.message_controllers import (
    get_conversation,
    send_message,
)
from response_operations_ui.exceptions.exceptions import InternalError
from response_operations_ui.views.messages import (
    _get_to_id,
    _get_unread_status,
    _verify_requested_page_is_within_bounds,
)
from tests.views import ViewTestCase

respondent_party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
collection_exercise_id_1 = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
collection_exercise_id_2 = "9af403f8-5fc5-43b1-9fca-afbd9c65da5c"
survey_id_1 = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_id_2 = "6aa8896f-ced5-4694-800c-6cd661b0c8b2"
survey_id_3 = "02b9c366-7397-42f7-942a-76dc5876d86d"
ru_ref = "50012345678"
iac_1 = "jkbvyklkwj88"
iac_2 = "ljbgg3kgstr4"

url_get_business_by_ru_ref = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/ref/"
url_get_business_by_id = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/"
url_get_respondent_party_by_list = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents?id={respondent_party_id}"
url_get_respondent_party_by_id = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/"
url_get_business_attributes = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/id/{business_party_id}/attributes"

shortname_url = f"{TestingConfig.SURVEY_URL}/surveys/shortname"
url_get_surveys_list = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"
url_get_survey_by_id = f"{TestingConfig.SURVEY_URL}/surveys/{survey_id_1}"
url_get_survey_by_id_3 = f"{TestingConfig.SURVEY_URL}/surveys/{survey_id_3}"

url_get_thread = f"{TestingConfig.SECURE_MESSAGE_URL}/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af"
url_get_threads_list = f"{TestingConfig.SECURE_MESSAGE_URL}/threads"
url_send_message = f"{TestingConfig.SECURE_MESSAGE_URL}/messages"
url_messages = f"{TestingConfig.SECURE_MESSAGE_URL}/messages"
url_update_label = f"{TestingConfig.SECURE_MESSAGE_URL}/messages/modify/ae46748b-c6e6-4859-a57a-86e01db2dcbc"
url_modify_label_base = f"{TestingConfig.SECURE_MESSAGE_URL}/messages/modify/"
url_select_survey = f"{TestingConfig.SECURE_MESSAGE_URL}/messages/select-survey"

url_sign_in_data = f"{TestingConfig.UAA_SERVICE_URL}/oauth/token"
url_permission_url = f"{TestingConfig.UAA_SERVICE_URL}/Users/test-id"
url_get_case_groups_by_business_party_id = f"{TestingConfig.CASE_URL}/cases/partyid/{business_party_id}"
url_get_collection_exercise_by_id = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_get_iac = f"{TestingConfig.IAC_URL}/iacs"

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/message/thread.json") as json_data:
    thread_json = json.load(json_data)
with open(f"{project_root}/test_data/message/thread_missing_subject.json") as json_data:
    thread_missing_subject = json.load(json_data)
with open(f"{project_root}/test_data/message/threads.json") as json_data:
    thread_list = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_multipage.json") as json_data:
    thread_list_multi_page = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_multipage_multi_ru.json") as json_data:
    thread_list_multi_page_multi_ru = json.load(json_data)
with open(f"{project_root}/test_data/survey/survey_list.json") as json_data:
    survey_list = json.load(json_data)
with open(f"{project_root}/test_data/survey/ashe_response.json") as json_data:
    ashe_info = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_no_unread.json") as json_data:
    threads_no_unread_list = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_unread.json") as json_data:
    threads_unread_list = json.load(json_data)
with open(f"{project_root}/test_data/message/thread_unread.json") as json_data:
    thread_unread_json = json.load(json_data)
with open(f"{project_root}/test_data/message/thread_unread_technical.json") as json_data:
    thread_unread_technical_json = json.load(json_data)
with open(f"{project_root}/test_data/message/thread_unread_rft.json") as json_data:
    thread_unread_rft_json = json.load(json_data)
with open(f"{project_root}/test_data/party/business_reporting_unit.json") as fp:
    business_reporting_unit = json.load(fp)
with open(f"{project_root}/test_data/party/get_business_by_ru_ref.json") as fp:
    business_by_ru_ref_json = json.load(fp)
with open(f"{project_root}/test_data/case/cases_list.json") as fp:
    cases_list = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as fp:
    collection_exercise = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise_2.json") as fp:
    collection_exercise_2 = json.load(fp)
with open(f"{project_root}/test_data/party/business_attributes.json") as fp:
    business_attributes = json.load(fp)
with open(f"{project_root}/test_data/party/business_party.json") as fp:
    business_party = json.load(fp)
with open(f"{project_root}/test_data/survey/single_survey.json") as fp:
    survey = json.load(fp)
with open(f"{project_root}/test_data/survey/survey_02b9c366.json") as fp:
    survey_02b9c366 = json.load(fp)
with open(f"{project_root}/test_data/party/respondent_party.json") as fp:
    respondent_party = json.load(fp)
with open(f"{project_root}/test_data/party/respondent_party_list.json") as fp:
    respondent_party_list = json.load(fp)
with open(f"{project_root}/test_data/iac/iac.json") as fp:
    iac = json.load(fp)
with open(f"{project_root}/test_data/message/threads_missing_atmsg_to.json") as json_data:
    threads_missing_atmsg_to_json = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_missing_atmsg_from.json") as json_data:
    threads_missing_atmsg_from_json = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_missing_msg_to.json") as json_data:
    threads_missing_msg_to_json = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_missing_ru_ref.json") as json_data:
    threads_missing_ru_ref_json = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_missing_sent_date.json") as json_data:
    threads_missing_sent_date_json = json.load(json_data)
with open(f"{project_root}/test_data/message/threads_missing_business_name.json") as json_data:
    threads_missing_business_name_json = json.load(json_data)
with open(f"{project_root}/test_data/message/thread_missing_respondent.json") as json_data:
    missing_user_json = json.load(json_data)


user_permission_admin_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "uaa.user", "type": "DIRECT"}],
}
user_permission_messages_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "messages.edit", "type": "DIRECT"}],
}


def sign_in_with_permission(self, mock_request, permission):
    mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
    mock_request.get(url_permission_url, json=permission, status_code=200)
    self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})


class TestMessage(ViewTestCase):
    def setup_data(self):
        self.surveys_list_json = [
            {
                "id": "f235e99c-8edf-489a-9c72-6cabe6c387fc",
                "shortName": "ASHE",
                "longName": "ASHE long name",
                "surveyRef": "123",
            }
        ]
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.before()

    def before(self):
        self.mock_uaa()
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )
        # sign-in to setup the user in the session
        self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})

    @requests_mock.mock()
    def mock_uaa(self, mock_request):
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_threads_list(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Apple".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)
        self.assertIn("John Example".encode(), response.data)
        self.assertIn("ASHE Team".encode(), response.data)
        self.assertIn("Message from respondent".encode(), response.data)
        self.assertIn("Message from ONS".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_technical_inbox_threads_list(self, mock_request, mock_get_jwt):
        """
        Tests if the right messages get displayed for the technical inbox.  This will look very similar to the
        survey one for now until we have a way to create technical messages and/or be able to switch the categories
        of the messages.  Once we do, we can know what the requirements are (i.e., will messages of certain categories
        have survey, business and collection exercise information?)
        """
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/technical", json=ashe_info["survey"])
        response = self.client.get("/messages/technical")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Technical Messages".encode(), response.data)
        self.assertIn("Change inbox".encode(), response.data)
        self.assertIn("johnexample@example.com".encode(), response.data)
        self.assertIn("John Example".encode(), response.data)
        self.assertIn("Message from respondent".encode(), response.data)
        self.assertIn(
            'href="/respondents/respondent-details/ff4537df-2097-4a73-a530-e98dba7bf28f"'.encode(), response.data
        )

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_rft_inbox_selection(self, mock_request, mock_get_jwt):
        """
        Tests if the right messages get displayed for the RFT inbox.
        """
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/miscellaneous", json=ashe_info["survey"])
        form = {"inbox-radio": "misc"}
        response = self.client.post("/messages/select-survey", data=form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("RFT Messages".encode(), response.data)
        self.assertNotIn("Apple".encode(), response.data)
        self.assertNotIn("50012345678".encode(), response.data)
        self.assertIn("John Example".encode(), response.data)
        self.assertIn("Message from respondent".encode(), response.data)
        self.assertIn("johnexample@example.com".encode(), response.data)
        self.assertIn(
            'href="/respondents/respondent-details/ff4537df-2097-4a73-a530-e98dba7bf28f"'.encode(), response.data
        )

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_rft_inbox_threads_list(self, mock_request, mock_get_jwt):
        """
        Tests if the right messages get displayed for the RFT inbox.
        """
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/miscellaneous", json=ashe_info["survey"])
        response = self.client.get("/messages/miscellaneous")

        self.assertEqual(response.status_code, 200)
        self.assertIn("RFT Messages".encode(), response.data)
        self.assertNotIn("Apple".encode(), response.data)
        self.assertNotIn("50012345678".encode(), response.data)
        self.assertIn("John Example".encode(), response.data)
        self.assertIn("ASHE Team".encode(), response.data)
        self.assertIn("Message from respondent".encode(), response.data)
        self.assertIn("Message from ONS".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_survey_short_name_failure(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(shortname_url + "/ASHE", status_code=500)
        response = self.client.get("/messages/ASHE", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_threads_list_missing_data(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])

        # Missing atmsg_to
        mock_request.get(url_get_threads_list, json=threads_missing_atmsg_to_json)
        response = self.client.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Deleted respondent".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

        # Missing atmsg_from
        mock_request.get(url_get_threads_list, json=threads_missing_atmsg_from_json)
        response = self.client.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Deleted respondent".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

        # Missing msg_to
        mock_request.get(url_get_threads_list, json=threads_missing_msg_to_json)
        response = self.client.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

        # Missing ru_ref
        mock_request.get(url_get_threads_list, json=threads_missing_ru_ref_json)
        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

        # Missing date
        mock_request.get(url_get_threads_list, json=threads_missing_sent_date_json)
        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

        # Missing business name
        mock_request.get(url_get_threads_list, json=threads_missing_business_name_json)
        response = self.client.get("/messages/ASHE")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unavailable".encode(), response.data)
        self.assertIn("Example message subject".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_threads_list_fail(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, status_code=500)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        response = self.client.get("/messages/ASHE", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_threads_list_empty(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        # If response doesn't have a messages key then it shouldn't give a server error,
        # but instead log the problem and display an empty inbox to the user.

        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json={"messages": []})
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("No new conversations".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_conversation_count_response_error(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=500)
        response = self.client.get("/messages/ASHE", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_read_messages_are_displayed_correctly(self, mock_request):
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=threads_no_unread_list)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        response = self.client.get("/messages/ASHE")

        self.assertNotIn("message-list__item--unread".encode(), response.data)
        self.assertNotIn("circle-icon".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_unread_messages_are_displayed_correctly(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=threads_unread_list)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        response = self.client.get("/messages/ASHE")

        self.assertIn("status".encode(), response.data)

    def test_get_message_unread_status(self):
        unread_message = {"labels": ["INBOX", "UNREAD"]}
        self.assertTrue(_get_unread_status(unread_message))

        read_message = {"labels": ["INBOX"]}
        self.assertFalse(_get_unread_status(read_message))

        message_missing_labels = {}
        self.assertFalse(_get_unread_status(message_missing_labels))

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_thread_success(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)

        # Survey messages
        mock_request.get(url_get_thread, json=thread_unread_json)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
        self.assertIn("Unread Message Subject".encode(), response.data)
        self.assertIn("Mark as unread".encode(), response.data)

        # Technical messages
        mock_request.get(url_get_thread, json=thread_unread_technical_json)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
        self.assertIn("Unread Message Subject".encode(), response.data)
        self.assertIn("Category".encode(), response.data)
        self.assertIn("TECHNICAL".encode(), response.data)

        # RFT messages
        mock_request.get(url_get_thread, json=thread_unread_rft_json)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
        self.assertIn("Unread Message Subject".encode(), response.data)
        self.assertIn("Category".encode(), response.data)
        self.assertIn("MISC".encode(), response.data)

    @requests_mock.mock()
    def test_open_thread_with_deleted_respondent(self, mock_request):
        response = self._get_thread_with_deleted_respondent(mock_request, missing_user_json)
        self.assertIn("You can no longer send a message as this respondent has been deleted".encode(), response.data)
        self.assertIn("Close conversation".encode(), response.data)

    @requests_mock.mock()
    def test_closed_thread_with_deleted_respondent(self, mock_request):
        missing_user_json_closed_thread = missing_user_json.copy()
        missing_user_json_closed_thread["is_closed"] = True
        missing_user_json_closed_thread["closed_by"] = "fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af"
        response = self._get_thread_with_deleted_respondent(mock_request, missing_user_json_closed_thread)
        self.assertIn(
            "This conversation can not be re-opened as the respondent has been deleted".encode(), response.data
        )
        self.assertNotIn("Close conversation".encode(), response.data)

    @requests_mock.mock()
    def test_open_thread_with_deleted_respondent_which_never_responded(self, mock_request):
        missing_user_json_no_response = missing_user_json.copy()
        missing_user_json_no_response["messages"].pop(0)
        response = self._get_thread_with_deleted_respondent(mock_request, missing_user_json_no_response)
        self.assertIn("You can no longer send a message as this respondent has been deleted".encode(), response.data)
        self.assertIn("Close conversation".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_thread_sent_to_different_user_mark_unread_not_displayed(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        test_data = copy.deepcopy(thread_unread_json)
        test_data["messages"][0]["msg_to"] = ["SomeoneElse"]
        mock_request.get(url_get_thread, json=test_data)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertNotIn("Mark as unread".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_read_thread_sent_to_same_user_mark_unread_displayed(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_get_jwt.return_value = "blah"
        test_data = copy.deepcopy(thread_unread_json)
        test_data["messages"][0]["msg_to"] = ["test-id"]
        mock_request.get(url_get_thread, json=test_data)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertIn("Mark as unread".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_thread_when_update_label_fails(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label, status_code=500)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertIn("Unread Message Subject".encode(), response.data)

    def test_get_conversation_fail_when_no_configuration_key(self):
        with self.app.app_context():
            self.app.config.pop("SECURE_MESSAGE_URL")

            with self.assertRaises(KeyError):
                get_conversation("test123")

    message_json = """
        {
          "msg_from": "BRES",
          "msg_to": ["f62dfda8-73b0-4e0e-97cf-1b06327a6712"],
          "subject": "TEST SUBJECT",
          "body": "TEST MESSAGE",
          "thread_id": "",
          "case_id": "",
          "survey_id": "BRES2017",
          "business_id": "c614e64e-d981-4eba-b016-d9822f09a4fb"
        }
        """

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_request_response_malformed(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_threads_list, json={})
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        response = self.client.get("/messages/ASHE")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong".encode(), response.data)

    @requests_mock.mock()
    def test_send_message_fail(self, mock_request):
        with self.app.app_context():
            self.app.config.pop("SECURE_MESSAGE_URL")
            url = url_send_message
            mock_request.post(url)

            with self.assertRaises(InternalError):
                send_message(self.message_json)

    ru_details = {
        "create-message": "create-message-view",
        "survey": "BRES 2017",
        "survey_id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
        "ru_ref": "49900000280",
        "business": "Bolts & Rachets Ltd",
        "msg_to_name": "Jacky Turner",
        "msg_to": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
        "business_id": "c614e64e-d981-4eba-b016-d9822f09a4fb",
    }

    @requests_mock.mock()
    def test_details_fields_prepopulated(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        response = self.client.post("/messages/create-message", data=self.ru_details)

        self.assertIn("BRES 2017".encode(), response.data)
        self.assertIn("49900000280".encode(), response.data)
        self.assertIn("Bolts &amp; Rachets Ltd".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)

    @requests_mock.mock()
    def test_empty_subject_and_body_rejected(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        response = self.client.post("/messages/create-message")

        self.assertIn("Please enter a subject".encode(), response.data)
        self.assertIn("Please enter a message".encode(), response.data)

    message_form = {"body": "TEST BODY", "subject": "TEST SUBJECT", "hidden_survey": "ASHE", "hidden_ru_ref": ru_ref}
    FDI_message = {"body": "AIFDI BODY", "subject": "AIFDI SUBJECT", "hidden_survey": "AIFDI", "hidden_ru_ref": ru_ref}
    AIFDI_response = {
        "id": "41320b22-b425-4fba-a90e-718898f718ce",
        "shortName": "AIFDI",
        "longName": "Annual Inward Foreign Direct Investment Survey",
        "surveyRef": "062",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947",
        "surveyMode": "SEFT",
    }
    AOFDI_response = {
        "id": "04dbb407-4438-4f89-acc4-53445d75330c",
        "shortName": "AOFDI",
        "longName": "Annual Outward Foreign Direct Investment Survey",
        "surveyRef": "063",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947",
        "surveyMode": "SEFT",
    }
    QIFDI_response = {
        "id": "c3eaeff3-d570-475d-9859-32c3bf87800d",
        "shortName": "QIFDI",
        "longName": "Quarterly Inward Foreign Direct Investment Survey",
        "surveyRef": "064",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947",
        "surveyMode": "SEFT",
    }
    QOFDI_response = {
        "id": "57a43c94-9f81-4f33-bad8-f94800a66503",
        "shortName": "QOFDI",
        "longName": "Quarterly Outward Foreign Direct Investment Survey",
        "surveyRef": "065",
        "legalBasis": "Statistics of Trade Act 1947",
        "surveyType": "Business",
        "legalBasisRef": "STA1947",
        "surveyMode": "SEFT",
    }

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("flask_login.utils._get_user")
    def test_form_submit_with_valid_data(self, mock_request, current_user, mock_get_jwt):
        self.before()
        mock_get_jwt.return_value = "blah"
        mock_request.post(url_send_message, json=threads_no_unread_list, status_code=201)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_business_by_ru_ref + ru_ref, json=business_by_ru_ref_json)
        mock_request.get(url_get_case_groups_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        current_user.return_value.id = 1
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        with self.app.app_context():
            response = self.client.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message sent.".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("flask_login.utils._get_user")
    def test_form_submit_with_FDI_data(self, mock_request, current_user, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.post(url_send_message, json=threads_no_unread_list, status_code=201)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_business_by_ru_ref + ru_ref, json=business_by_ru_ref_json)
        mock_request.get(url_get_case_groups_by_business_party_id, json=cases_list)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_1}", json=collection_exercise)
        mock_request.get(f"{url_get_collection_exercise_by_id}/{collection_exercise_id_2}", json=collection_exercise_2)
        mock_request.get(url_get_business_attributes, json=business_attributes)
        mock_request.get(url_get_survey_by_id, json=survey)
        mock_request.get(url_get_respondent_party_by_list, json=respondent_party_list)
        mock_request.get(f"{url_get_iac}/{iac_1}", json=iac)
        mock_request.get(f"{url_get_iac}/{iac_2}", json=iac)
        current_user.return_value.id = 1
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        with self.app.app_context():
            response = self.client.post("/messages/create-message", data=self.FDI_message, follow_redirects=True)

        self.assertIn("Message sent.".encode(), response.data)
        self.assertIn("Messages".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("flask_login.utils._get_user")
    def test_form_submitted_with_api_error(self, mock_request, current_user, mock_get_jwt):
        mock_request.post(url_send_message, status_code=500)
        mock_get_jwt.return_value = "blah"
        current_user.return_value.id = 1
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        with self.app.app_context():
            response = self.client.post("/messages/create-message", data=self.message_form, follow_redirects=True)

        self.assertIn("Message failed to send, something has gone wrong with the website.".encode(), response.data)
        self.assertIn("TEST SUBJECT".encode(), response.data)
        self.assertIn("TEST BODY".encode(), response.data)

    def test_link_post_details_malformed(self):
        malformed_ru_details = {"create-message": "create-message-view"}
        with self.assertRaises(Exception) as raises:
            self.client.post("/messages/create-message", data=malformed_ru_details)
            self.assertEqual(raises.exception.message, "Failed to load create message page")

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_change_reporting_unit(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_survey_by_id_3, json=survey_02b9c366)
        party_response = {
            "associations": [
                {
                    "businessRespondentStatus": "ACTIVE",
                    "enrolments": [{"enrolmentStatus": "ENABLED", "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"}],
                    "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
                    "sampleUnitRef": "49900000001",
                },
            ],
            "emailAddress": "example@example.com",
            "firstName": "john",
            "id": "0d7b3e2e-4c0c-4479-a002-09f8328f7292",
            "lastName": "doe",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "07772257772",
        }
        respondent_id = "0d7b3e2e-4c0c-4479-a002-09f8328f7292"
        mock_request.get(url_get_respondent_party_by_id + respondent_id, json=party_response)
        mock_request.get(url_get_business_by_id + business_party_id, json=business_party)

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/change-reporting-unit")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Assign a reporting unit to the thread".encode(), response.data)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.uaa_controller.user_has_permission")
    def test_conversation(self, mock_request, has_permission, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        has_permission.return_value = True
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Need more information on project".encode(), response.data)
        self.assertIn("Project ideas".encode(), response.data)
        self.assertIn("49900000001".encode(), response.data)
        self.assertIn("Apple".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_conversation_reply_fail(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        response = self.client.post("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter a message".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_conversation_fail(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, status_code=500)

        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("flask_login.utils._get_user")
    def test_conversation_reply(self, mock_request, current_user, mock_get_jwt):
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "ASHE"
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        mock_get_jwt.return_value = "blah"
        current_user.return_value.id = 1
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        # Post message on reply
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.post(url_send_message, json=threads_no_unread_list, status_code=201)

        # Conversation list
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        response = self.client.post(
            "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af", data=self.message_form, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("RU Ref".encode(), response.data)
        self.assertIn("Business name".encode(), response.data)
        self.assertIn("Subject".encode(), response.data)

    @requests_mock.mock()
    def test_conversation_decode_error(self, mock_request):
        mock_request.get(url_get_thread)
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 0)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("flask_login.utils._get_user")
    def test_conversation_key_error(self, mock_request, current_user):
        mock_request.get(url_get_thread, json={})
        with self.client.session_transaction() as session:
            session["user_id"] = "test-id"
        current_user.return_value.id = 1
        mock_request.get(url_permission_url, json=user_permission_admin_json, status_code=200)
        mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_radio_buttons(self, mock_request):
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.client.get("/messages/select-survey")

        self.assertEqual(200, response.status_code)
        self.assertIn("Choose which messages to show".encode(), response.data)
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
        self.assertIn("Choose which messages to show".encode(), response.data)
        self.assertIn("Surveys".encode(), response.data)

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
        self.assertIn("Choose which messages to show".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_messages_page_with_survey(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])

        response = self.client.post(
            "/messages/select-survey", follow_redirects=True, data={"inbox-radio": "surveys", "select-survey": "ASHE"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("ASHE Messages".encode(), response.data)

        response = self.client.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("ASHE Messages".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_messages_page_with_FDI_survey(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)
        mock_request.get(url_get_surveys_list, json=survey_list)

        # Mocking FDI responses
        mock_request.get(shortname_url + "/QIFDI", json=self.QIFDI_response)
        mock_request.get(shortname_url + "/QOFDI", json=self.QOFDI_response)
        mock_request.get(shortname_url + "/AIFDI", json=self.AIFDI_response)
        mock_request.get(shortname_url + "/AOFDI", json=self.AOFDI_response)

        response = self.client.post(
            "/messages/select-survey", follow_redirects=True, data={"inbox-radio": "surveys", "select-survey": "FDI"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("FDI Messages".encode(), response.data)

        response = self.client.get("/messages", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("FDI Messages".encode(), response.data)

    def test_get_to_id(self):
        self.assertEqual(thread_list["messages"][0]["msg_to"][0], _get_to_id(thread_list["messages"][0]))

    def test_get_to_id_index_error(self):
        with open(f"{project_root}/test_data/message/threads.json") as fp:
            conversation = json.load(fp)
        del conversation["messages"][0]["msg_to"][0]
        self.assertEqual(None, _get_to_id(conversation["messages"][0]))

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_close_conversation_confirmation_page_for_survey(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "QBS"
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)

        response = self.client.get(
            "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation?category=SURVEY",
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn("Subject".encode(), response.data)
        self.assertIn("Business".encode(), response.data)
        self.assertIn("Reference".encode(), response.data)
        self.assertIn("Respondent".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_close_conversation_confirmation_page_for_categories(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = ""
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)

        # Technical
        response = self.client.get(
            "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation?category=TECHNICAL",
            follow_redirects=True,
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Category".encode(), response.data)
        self.assertNotIn("Business".encode(), response.data)
        self.assertNotIn("Reference".encode(), response.data)
        self.assertIn("Respondent".encode(), response.data)

        # Misc
        response = self.client.get(
            "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation?category=MISC",
            follow_redirects=True,
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Category".encode(), response.data)
        self.assertNotIn("Business".encode(), response.data)
        self.assertNotIn("Reference".encode(), response.data)
        self.assertIn("Respondent".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_close_conversation(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        response = self.client.post(
            "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation", follow_redirects=True
        )

        self.assertEqual(200, response.status_code)
        self.assertIn("Conversation closed".encode(), response.data)
        self.assertIn("Ashe Messages".encode(), response.data)
        self.assertIn("John Example".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_close_conversation_http_error(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.patch(url_get_thread, json=thread_json, status_code=500)

        response = self.client.post(
            "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af/close-conversation", follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_reopen_conversation(self, mock_request, mock_get_jwt):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        with self.app.app_context():
            response = self.client.post(
                "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af",
                data={"reopen": "Re-open conversation"},
                follow_redirects=True,
            )

        self.assertEqual(200, response.status_code)
        self.assertIn("Conversation re-opened.".encode(), response.data)
        self.assertIn("Ashe Messages".encode(), response.data)

    @requests_mock.mock()
    def test_reopen_conversation_technical_messages(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "technical"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        with self.app.app_context():
            response = self.client.post(
                "/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af?category=TECHNICAL",
                data={"reopen": "Re-open conversation"},
                follow_redirects=True,
            )

        self.assertEqual(200, response.status_code)
        self.assertIn("Conversation re-opened.".encode(), response.data)
        self.assertIn("Technical Messages".encode(), response.data)

    def test_calculate_page_change(self):
        result = _verify_requested_page_is_within_bounds(3, 10, 15)
        self.assertEqual(2, result)

    def test_calculate_page_no_change(self):
        result = _verify_requested_page_is_within_bounds(1, 10, 15)
        self.assertEqual(1, result)

    def test_calculate_page_zero_threads(self):
        result = _verify_requested_page_is_within_bounds(1, 10, 0)
        self.assertEqual(1, result)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_mark_unread_returns_expected_flash_message(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "ASHE"

        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_get_threads_list, json=threads_no_unread_list)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.put(f"{url_modify_label_base}9ecfad50-2ff5-4bea-a997-d73c4faa73ae")

        response = self.client.get(
            "/messages/mark_unread/9ecfad50-2ff5-4bea-a997-d73c4faa73ae?from=GROUP&to=ONS+User", follow_redirects=True
        )

        self.assertIn("Message from GROUP to ONS User marked unread".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_closeing_conversation_returns_to_correct_tab_and_page(self, mock_request, mock_get_jwt):
        """
        For each tab check that if a conversation is closed then return to the same tab at the same page
        """
        limit = 10
        page = 2
        thread_id = "fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af"

        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_messages + "/count", json={"total": limit + 3}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page)

        conversation_tabs = ["my messages", "open", "closed", "initial"]
        for conversation_tab in conversation_tabs:
            with self.subTest(conversation_tab=conversation_tab):
                # issue same call as when closing a conversation whilst on page 2 of the selected tab
                url = f"{thread_id}/close-conversation?conversation_tab={conversation_tab}&page={page}&limit={limit}"
                response = self.client.post("/messages/threads/" + url, follow_redirects=True)

                response_body = response.data.decode("utf-8").replace(" ", "")

                self.assertEqual(200, response.status_code)

                # validate that the currently selected tab is as expected (i.e aria-current="location")
                match = (
                    f'"/messages/Ashe?conversation_tab={conversation_tab.replace(" ", "+")}'
                    f'&ru_ref_filter=&business_id_filter="aria-current="location"'
                )

                self.assertIn(match, response_body.replace("amp;", ""))

                # and that page 2 is selected
                self.assertIn('<liclass="ons-pagination__itemons-pagination__item--current">', response_body)
                self.assertIn('aria-label="Currentpage(Page2of2)"', response_body)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_closing_conversation_returns_to_previous_tab_if_page_is_now_too_high(self, mock_request, mock_get_jwt):
        """if a conversation is closed then it will disappear from some tabs. That could mean that the page number
        specified is now too high, this test validates that if that is the case then the previous page is used"""

        limit = 10
        page = 4
        thread_id = "fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af"

        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        # Returned count is less than 4 pages worth
        mock_request.get(url_messages + "/count", json={"total": (limit * (page - 1)) - 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page)

        conversation_tabs = ["my messages", "open", "initial"]  # Cant close a thread in the closed tab
        for conversation_tab in conversation_tabs:
            with self.subTest(conversation_tab=conversation_tab):
                # issue same call as when closing a conversation whilst on page 4 of the selected tab
                url = f"{thread_id}/close-conversation?conversation_tab={conversation_tab}&page={page}&limit={limit}"
                response = self.client.post("/messages/threads/" + url, follow_redirects=True)

                response_body = response.data.decode("utf-8").replace(" ", "")

                self.assertEqual(200, response.status_code)

                # validate that the currently selected tab is as expected (i.e aria-current="location")
                match = (
                    f'"/messages/Ashe?conversation_tab={conversation_tab.replace(" ", "+")}'
                    f'&ru_ref_filter=&business_id_filter="aria-current="location"'
                )
                self.assertIn(match, response_body.replace("amp;", ""))

                # and that page 3 is selected
                self.assertIn('<liclass="ons-pagination__itemons-pagination__item--current">', response_body)
                self.assertIn('aria-label="Currentpage(Page3of3)"', response_body)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_reopening_conversation_returns_to_closed_tab(self, mock_request, mock_get_jwt):
        limit = 10
        page = 4
        thread_id = "fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af"

        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        mock_request.patch(url_get_thread, json=thread_json)
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_messages + "/count", json={"total": 1}, status_code=200)
        mock_request.get(url_get_threads_list, json=thread_list)

        url = f"/messages/threads/{thread_id}?page={page}&limit={limit}&conversation_tab=closed"
        response = self.client.post(url, data={"reopen": "Re-open conversation"}, follow_redirects=True)

        response_body = response.data.decode("utf-8").replace(" ", "")

        # validate that the currently selected tab is as expected (i.e aria-current="location")
        match_str = '"aria-current="location">Closed'
        self.assertIn(match_str, response_body)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_all_conversation_type_counts")
    @patch("response_operations_ui.views.messages._get_tab_titles")
    def test_filter_threads_limits_by_ru_on_post(self, mock_request, mock_get_titles, mock_get_count, mock_get_jwt):
        """Validate that business_id_filter is passed as a parameter to get count and get messages
        And that the expected call to get by ru_ref from party is called after passing validation
        and that ru_ref_filter and business_id_filter parameters are present
        It is a function of secure message to actually return the correct messages"""
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref_filter = "12345678901"
        conversation_tab = "closed"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_get_titles.return_value = {
            "my messages": "My messages",
            "open": "Open",
            "closed": "Closed",
            "initial": "Initial",
        }
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        party_get_by_ru_ref = f"{url_get_business_by_ru_ref}{ru_ref_filter}"
        mock_request.get(party_get_by_ru_ref, json={"id": business_id_filter})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = {"current": 2, "open": 1, "closed": 2, "initial": 3, "my messages": 4}

        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}"
        )
        response = self.client.post(url, follow_redirects=True, json={"ru_ref_filter": ru_ref_filter})
        response_body = response.data.decode("utf-8").replace(" ", "")

        self.assertEqual(200, response.status_code)
        mock_get_count.assert_called_with(
            survey_id=["6aa8896f-ced5-4694-800c-6cd661b0c8b2"],
            business_id=business_id_filter,
            conversation_tab=conversation_tab,
            category="SURVEY",
        )

        query = (
            f"is_closed=true&my_conversations=false&new_respondent_conversations=false&category=survey"
            f"&all_conversation_types=false&business_id={business_id_filter}&survey={survey_id_2}"
            f"&page={page}&limit={limit}"
        )
        assert self._mock_request_called_with_expected_query(mock_request, query)

        assert self._mock_request_called_with_expected_path(mock_request, party_get_by_ru_ref)

        assert "ru_ref_filter" in response_body
        assert "business_id" in response_body

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_conversation_count")
    def test_filter_threads_limits_by_ru_on_get(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that business_id_filter is passed as a parameter to get count and get messages
        and that ru_ref_filter and business_id_filter parameters are present
        It is a function of secure message to actually return the correct messages"""
        limit = 15
        page = 1
        business_id_filter = "123"
        conversation_tab = "closed"
        category = "SURVEY"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}"
        )
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8").replace(" ", "")

        self.assertEqual(200, response.status_code)
        mock_get_count.assert_called_with(
            survey_id=["6aa8896f-ced5-4694-800c-6cd661b0c8b2"],
            business_id=business_id_filter,
            conversation_tab=conversation_tab,
            category=category,
        )

        query = (
            f"is_closed=true&my_conversations=false&new_respondent_conversations=false&category=survey"
            f"&all_conversation_types=false&business_id={business_id_filter}&survey={survey_id_2}"
            f"&page={page}&limit={limit}"
        )
        assert self._mock_request_called_with_expected_query(mock_request, query)

        assert "ru_ref_filter" in response_body
        assert "business_id_filter" in response_body

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_all_conversation_type_counts")
    @patch("response_operations_ui.views.messages._get_tab_titles")
    def test_filter_threads_clear_filter_displayed_when_filter_active(
        self, mock_request, mock_get_titles, mock_get_count, mock_get_jwt
    ):
        """Validate that when the filter is in operation the clear filter is displayed"""
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref_filter = "12345678901"
        conversation_tab = "closed"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_get_titles.return_value = {
            "my messages": "My messages",
            "open": "Open",
            "closed": "Closed",
            "initial": "Initial",
        }
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        party_get_by_ru_ref = f"{url_get_business_by_ru_ref}{ru_ref_filter}"
        mock_request.get(party_get_by_ru_ref, json={"id": business_id_filter})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = {"current": 2, "open": 1, "closed": 2, "initial": 3, "my messages": 4}

        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}"
        )

        response = self.client.post(url, follow_redirects=True, json={"ru_ref_filter": ru_ref_filter})
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert f"Filtered by RU ref: {ru_ref_filter}" in response_body

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_conversation_count")
    def test_filter_threads_no_clear_filter_when_filter_not_active(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that when the filter is cleared via the clear filter link then the
        clear filter link is removed"""
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref = "12345678901"
        conversation_tab = "closed"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        mock_request.get(url_get_business_by_ru_ref + ru_ref, json={"id": business_id_filter})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # Call clear filter endpoint , passing in ru ref and business id
        url = (
            f"/messages/clear_filter/Ashe?page={page}&limit={limit}&"
            f"conversation_tab={conversation_tab}&business_id_filter={business_id_filter}&ru_ref={ru_ref}"
        )
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert "Filtered by RU ref" not in response_body

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_conversation_count")
    def test_filter_threads_display_flash_if_ru_ref_unknown(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that flash message is displayed when ru ref is not known and filter applied"""
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref_filter = "12345678901"
        conversation_tab = "closed"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        party_get_by_ru_ref = f"{url_get_business_by_ru_ref}{ru_ref_filter}"
        mock_request.get(party_get_by_ru_ref, status_code=404)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}"
        )
        response = self.client.post(url, follow_redirects=True, json={"ru_ref_filter": ru_ref_filter})
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert 'id="flashed-message-1' in response_body

        assert f"Filter not applied: {ru_ref_filter} is an unknown RU ref" in response_body

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_conversation_count")
    def test_filter_threads_display_flash_if_party_errors(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that flash message is displayed when ru ref is not known and filter applied"""
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref_filter = "12345678901"
        conversation_tab = "closed"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        party_get_by_ru_ref = f"{url_get_business_by_ru_ref}{ru_ref_filter}"
        mock_request.get(party_get_by_ru_ref, status_code=500)
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}"
        )
        response = self.client.post(url, follow_redirects=True, json={"ru_ref_filter": ru_ref_filter})
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)

        assert 'id="flashed-message-1' in response_body

        assert "Could not resolve RU ref, please try again later" in response_body

    def test_message_no_new_conversations_displayed_on_empty_open_tab(self):
        """Validate that No new conversations displayed on empty open tab"""
        self._validate_no_messages_text("open", "No new conversations")

    def test_message_no_new_conversations_displayed_on_empty_closed_tab(self):
        """Validate that No closed conversations displayed on empty closed tab"""
        self._validate_no_messages_text("closed", "No closed conversations")

    def test_message_no_new_conversations_displayed_on_empty_my_conversations_tab(self):
        """Validate that No closed conversations displayed on empty my conversations tab"""
        self._validate_no_messages_text("my messages", "There are currently no messages")

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_conversation_count")
    def _validate_no_messages_text(self, conversation_tab, expected_text, mock_request, mock_get_count, mock_get_jwt):
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref_filter = "12345678901"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"
        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])
        # Party returns no data so flash should display later
        mock_request.get(url_get_business_by_ru_ref + ru_ref_filter, json={"id": ""})
        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json={"messages": []})
        mock_get_count.return_value = 0
        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}&ru_ref={ru_ref_filter}"
        )
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)
        self.assertIn(expected_text, response_body)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_conversation_count")
    def test_messages_tabs_are_displayed(self, mock_request, mock_get_count, mock_get_jwt):
        """Validate that the expected tabs are in the returned html"""
        limit = 15
        page = 1
        business_id_filter = "123"
        conversation_tab = "closed"

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = 10

        # view survey with filter of business_id
        url = (
            f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
            f"&business_id_filter={business_id_filter}"
        )
        response = self.client.get(url, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)
        self.assertIn('href="/messages/Ashe?conversation_tab=my+messages', response_body)
        self.assertIn('href="/messages/Ashe?conversation_tab=open', response_body)
        self.assertIn('href="/messages/Ashe?conversation_tab=closed', response_body)
        self.assertIn('href="/messages/Ashe?conversation_tab=initial', response_body)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_messages_survey_dropdown_displayed_on_select_survey_page(self, mock_request, mock_get_jwt):
        """Validate that the survey drop down is in the returned"""

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)

        response = self.client.get(url_select_survey, follow_redirects=True)
        response_body = response.data.decode("utf-8")

        self.assertEqual(200, response.status_code)
        self.assertIn('id="survey-list"', response_body)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    @patch("response_operations_ui.controllers.message_controllers.get_all_conversation_type_counts")
    def test_titles_show_count_and_correct_tab_selected_when_filter_active(
        self, mock_request, mock_get_count, mock_get_jwt
    ):
        limit = 15
        page = 1
        business_id_filter = "123"
        ru_ref_filter = "12345678901"

        tabs = ["closed", "closed", "initial", "my messages"]

        with self.client.session_transaction() as session:
            session["messages_survey_selection"] = "Ashe"
        mock_get_jwt.return_value = "blah"

        mock_request.get(shortname_url + "/ASHE", json=ashe_info["survey"])

        mock_request.get(url_get_surveys_list, json=self.surveys_list_json)
        mock_request.get(url_get_threads_list, json=thread_list_multi_page_multi_ru)
        mock_get_count.return_value = {"current": 2, "open": 1, "closed": 2, "initial": 3, "my messages": 4}

        for conversation_tab in tabs:
            with self.subTest(conversation_tab=conversation_tab):
                # view survey with filter of business_id

                url = (
                    f"/messages/Ashe?page={page}&limit={limit}&conversation_tab={conversation_tab}"
                    f"&business_id_filter={business_id_filter}&ru_ref_filter={ru_ref_filter}"
                )
                response = self.client.get(url, follow_redirects=True)
                response_body = response.data.decode("utf-8")

                self.assertEqual(200, response.status_code)

                # Validate correct counts are displayed on each tab

                self.assertIn("Open (1)", response_body)
                self.assertIn("Closed (2)", response_body)
                self.assertIn("Initial (3)", response_body)
                self.assertIn("My messages (4)", response_body)

                # Validate correct tab selected

                self.assertIn(
                    f'aria-current="location">{conversation_tab.replace(" ", "")}',
                    response_body.lower().replace(" ", ""),
                )

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_conversation_reply_no_edit_permission(self, mock_request, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        mock_request.get(url_get_thread, json=thread_unread_json)
        mock_request.put(url_update_label)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Reply".encode(), response.data)
        self.assertNotIn("Close conversation".encode(), response.data)
        self.assertNotIn("Send message".encode(), response.data)

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

    def _get_thread_with_deleted_respondent(self, mock_request, user_json):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_request.get(url_get_thread, json=user_json)
        mock_request.get(url_get_surveys_list, json=survey_list)
        response = self.client.get("/messages/threads/fb0e79bd-e132-4f4f-a7fd-5e8c6b41b9af")
        return response


class MockUser:
    id = 1
