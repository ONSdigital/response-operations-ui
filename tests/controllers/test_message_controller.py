import unittest
from unittest.mock import patch

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers.message_controllers import (
    get_all_conversation_type_counts,
    patch_message,
    patch_thread,
)
from response_operations_ui.exceptions.exceptions import ApiError

msg_id = "06025b5a-26e4-4391-8e3c-c5b7b2ab53bd"
thread_id = "4899be9d-6641-4c0f-8cf4-7727542ff00c"
survey_id = "b9f84e0b-cb6b-4fd2-9a1a-43d9d85bad2b"

url_get_message_counts = f"{TestingConfig.SECURE_MESSAGE_URL}/messages/count"
url_get_message_patch = f"{TestingConfig.SECURE_MESSAGE_URL}/messages/{msg_id}"
url_get_thread_patch = f"{TestingConfig.SECURE_MESSAGE_URL}/threads/{thread_id}"


class TestMessageController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_all_conversation_type_counts_translates_tab_titles_when_all_zero_values(self, mock_get_jwt):
        mock_counts = {
            "totals": {"open": 0, "closed": 0, "new_respondent_conversations": 0, "my_conversations": 0, "current": 0}
        }
        mock_get_jwt.return_value = "blah"

        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.GET, url_get_message_counts, json=mock_counts, status=200)
            with self.app.app_context():
                totals = get_all_conversation_type_counts("ASurveyId", "initial", "a party id", "category")

            self.assertEqual(totals["initial"], 0)
            self.assertEqual(totals["my messages"], 0)

    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_all_conversation_type_counts_translates_tab_titles_when_non_zero_values(self, mock_get_jwt):
        mock_counts = {
            "totals": {"open": 0, "closed": 1, "new_respondent_conversations": 2, "my_conversations": 3, "current": 2}
        }
        mock_get_jwt.return_value = "blah"

        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.GET, url_get_message_counts, json=mock_counts, status=200)
            with self.app.app_context():
                totals = get_all_conversation_type_counts("ASurveyId", "initial", "a party id", "category")

            self.assertEqual(totals["initial"], 2)
            self.assertEqual(totals["my messages"], 3)

    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_patch_message_success(self, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.PATCH, url_get_message_patch, status=204)
            payload = {"survey_id": survey_id}
            with self.app.app_context():
                try:
                    patch_message(msg_id, payload)
                except Exception:  # noqa
                    self.fail("Exception shouldn't be getting thrown when a 204 is returned")

    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_patch_message_failure(self, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.PATCH, url_get_message_patch, status=400)
            payload = {"survey_id": survey_id}
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    patch_message(msg_id, payload)

    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_patch_thread_success(self, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.PATCH, url_get_thread_patch, status=204)
            payload = {"category": "TECHNICAL"}
            with self.app.app_context():
                try:
                    patch_thread(thread_id, payload)
                except Exception:  # noqa
                    self.fail("Exception shouldn't be getting thrown when a 204 is returned")

    @patch("response_operations_ui.controllers.message_controllers._get_jwt")
    def test_get_patch_thread_failure(self, mock_get_jwt):
        mock_get_jwt.return_value = "blah"
        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.PATCH, url_get_thread_patch, status=400)
            payload = {"category": "FAIL"}
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    patch_thread(thread_id, payload)
