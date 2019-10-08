import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.common import uaa


class TestUaa(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')

    def test_get_uaa_public_key_with_config_set(self):
        with self.app.app_context():
            self.assertEqual(TestingConfig.UAA_PUBLIC_KEY, uaa.get_uaa_public_key())

    @requests_mock.mock()
    def test_get_uaa_public_key_with_no_config_set(self, mock_request):
        mock_request.get(f'{self.app.config["UAA_SERVICE_URL"]}/token_key', json={'value': 'Test'})
        self.app.config["UAA_PUBLIC_KEY"] = None
        with self.app.app_context():
            self.assertEqual("Test", uaa.get_uaa_public_key())

    @requests_mock.mock()
    def test_get_uaa_public_key_server_error_response(self, mock_request):
        """When the getting of the public key fails a HTTPError exception is raised.  This test, however,
        assertIsNone because the exception is consumed, an exception is logged and then returns None.
        """
        mock_request.get(f'{self.app.config["UAA_SERVICE_URL"]}/token_key', status_code=500)
        self.app.config["UAA_PUBLIC_KEY"] = None
        with self.app.app_context():
            self.assertIsNone(uaa.get_uaa_public_key())

    @requests_mock.mock()
    def test_get_uaa_public_key_no_value_key(self, mock_request):
        """When there isn't a 'value' key in the returned json, a KeyError exception is raised.  This test, however,
        assertIsNone because the exception is consumed, an exception is logged and then returns None.
        """
        mock_request.get(f'{self.app.config["UAA_SERVICE_URL"]}/token_key', json={'notvalue': 'text'})
        self.app.config["UAA_PUBLIC_KEY"] = None
        with self.app.app_context():
            self.assertIsNone(uaa.get_uaa_public_key())
