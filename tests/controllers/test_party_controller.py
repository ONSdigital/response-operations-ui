import unittest
import mock
from collections import namedtuple

from response_operations_ui import create_app
from response_operations_ui.controllers.party_controller import search_respondents, get_respondent_by_party_ids
from response_operations_ui.exceptions.exceptions import SearchRespondentsException

fake_response = namedtuple('Response', 'status_code json')


class TestPartyController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    @mock.patch('requests.get')
    def test_import_search_respondents_raises_error_when_request_to_party_fails(self, requests_mock):
        with self.app.app_context():
            # Mock setups
            requests_mock.return_value = fake_response(status_code=400, json=lambda: [])
            limit = self.app.config["PARTY_RESPONDENTS_PER_PAGE"]
            # Test and assert
            with self.assertRaises(SearchRespondentsException):
                search_respondents('firstname', 'lastname', 'name@email.com', page=1, limit=limit)

    def test_get_respondent_by_party_ids_with_empty_list(self):
        input_data = []
        expected_output = []
        output = get_respondent_by_party_ids(input_data)
        self.assertEqual(output, expected_output)
