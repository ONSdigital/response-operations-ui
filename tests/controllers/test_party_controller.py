import unittest
import mock
from collections import namedtuple

from response_operations_ui import create_app
from response_operations_ui.controllers.party_controller import search_respondents, _get_search_respondents_url
from response_operations_ui.exceptions.exceptions import SearchRespondentsException

fake_response = namedtuple('Response', 'status_code json')


class TestPartyController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    @mock.patch('requests.get')
    @mock.patch('response_operations_ui.controllers.party_controller._get_search_respondents_url')
    def test_import_search_respondents_raises_error_when_request_to_party_fails(self, geturl, requests_mock):
        with self.app.app_context():
            # Mock setups
            geturl.return_value = 'TESTURL'
            requests_mock.return_value = fake_response(status_code=400, json=lambda: [])

            # Test and assert
            with self.assertRaises(SearchRespondentsException):
                search_respondents('firstname', 'lastname', 'name@email.com', 1)

    def test_get_respondents_url_returns_valid_url_based_on_app_config(self):
        with self.app.app_context():

            party_url = self.app.config.get('PARTY_URL', 'PARTYURL')
            limit = self.app.config.get('PARTY_RESPONDENTS_PER_PAGE', 25)

            expectation = f'{party_url}/party-api/v1/respondents?firstName=Bill&lastName=Gates&' \
                          f'emailAddress=bill@microsoft.com&page=1337&limit={limit}'
            url = _get_search_respondents_url(first_name="Bill", last_name="Gates", email_address="bill@microsoft.com",
                                              page=1337)
            self.assertEqual(url, expectation)

    def test_get_respondents_url_returns_string_not_including_invalid_query_args(self):
        with self.app.app_context():

            url = _get_search_respondents_url(first_name="Bill", last_name="Gates", email_address="bill@microsoft.com",
                                              page=1337, spurious_arg='spuriousness')
            self.assertFalse('spurious_arg=spuriousness' in url)
