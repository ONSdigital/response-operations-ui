import unittest
import mock

from response_operations_ui import create_app
from response_operations_ui.controllers.party_controller import search_respondents


class TestPartyController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    @mock.patch('response_operations_ui.controllers.party_controller.mock_search_respondents')
    @mock.patch('response_operations_ui.os.environ.get')
    def test_import_search_respondents_uses_mock_when_environment_variable_set(self, environ_get, mock_get):
        with self.app.app_context():
            environ_get.return_value = True

            search_respondents('firstname', 'lastname', 'name@email.com', 1)
            self.assertTrue(mock_get.called)

    @mock.patch('response_operations_ui.controllers.party_controller._get_search_respondents_url')
    @mock.patch('response_operations_ui.controllers.party_controller.mock_search_respondents')
    @mock.patch('response_operations_ui.os.environ.get')
    def test_import_search_respondents_doesnt_use_mock_when_environment_variable_unset(self, environ_get, mock_get, geturl):
        with self.app.app_context():
            environ_get.return_value = True
            geturl.return_value =

            search_respondents('firstname', 'lastname', 'name@email.com', 1)
            self.assertFalse(mock_get.called)


