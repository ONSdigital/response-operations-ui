import json
import responses
import unittest

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import admin_controller
from response_operations_ui.exceptions.exceptions import ApiError

url_banner = f'{TestingConfig.BANNER_SERVICE_URL}/banner'

banner_response = {'id': 'active', 'content': 'This is some text'}


class TestAdminController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    def test_get_banner_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_banner, json=banner_response, status=200, content_type='application/json')
            with self.app.app_context():
                response = admin_controller.current_banner()
                self.assertEqual(response, banner_response)

    def test_get_banner_not_found(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_banner, status=404)
            with self.app.app_context():
                response = admin_controller.current_banner()
                expected = {}
                self.assertEqual(response, expected)

    def test_get_banner_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_banner, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.current_banner()

