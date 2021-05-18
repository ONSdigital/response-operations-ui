import responses
import unittest

from config import TestingConfig
from response_operations_ui.controllers.message_controllers import get_all_conversation_type_counts
from response_operations_ui import create_app
from unittest.mock import patch

url_get_message_counts = f'{TestingConfig.SECURE_MESSAGE_URL}/messages/count'


class TestMessageController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_all_conversation_type_counts_translates_tab_titles_when_all_zero_values(self, mock_get_jwt):
        mock_counts = {'totals': {'open': 0,
                                  'closed': 0,
                                  'new_respondent_conversations': 0,
                                  'my_conversations': 0,
                                  'current': 0}}
        mock_get_jwt.return_value = "blah"

        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.GET, url_get_message_counts, json=mock_counts, status=200)
            with self.app.app_context():
                totals = get_all_conversation_type_counts('ASurveyId', 'initial', 'a party id', 'category')

            self.assertEqual(totals['initial'], 0)
            self.assertEqual(totals['my messages'], 0)

    @patch('response_operations_ui.controllers.message_controllers._get_jwt')
    def test_get_all_conversation_type_counts_translates_tab_titles_when_non_zero_values(self, mock_get_jwt):
        mock_counts = {'totals': {'open': 0,
                                  'closed': 1,
                                  'new_respondent_conversations': 2,
                                  'my_conversations': 3,
                                  'current': 2}}
        mock_get_jwt.return_value = "blah"

        with responses.RequestsMock() as mock_request:
            mock_request.add(mock_request.GET, url_get_message_counts, json=mock_counts, status=200)
            with self.app.app_context():
                totals = get_all_conversation_type_counts('ASurveyId', 'initial', 'a party id', 'category')

            self.assertEqual(totals['initial'], 2)
            self.assertEqual(totals['my messages'], 3)
