import unittest

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import admin_controller
from response_operations_ui.exceptions.exceptions import ApiError

url_banner = f'{TestingConfig.BANNER_SERVICE_URL}/banner'
url_template = f'{TestingConfig.BANNER_SERVICE_URL}/template'

banner_response = {'id': 'active', 'content': 'This is some text'}
set_banner_request = {'content': 'This is some text'}

template_1 = {'id': 1, 'title': 'Banner title 1', 'content': 'Banner content 1'}
template_2 = {'id': 2, 'title': 'Banner title 2', 'content': 'Banner content 2'}
templates_response = [template_1, template_2]


class TestAdminController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    # Banner tests

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

    def test_set_banner_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, url_banner, json=banner_response, status=201, content_type='application/json')
            with self.app.app_context():
                response = admin_controller.set_banner(set_banner_request)
                self.assertEqual(response, banner_response)

    def test_set_banner_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, url_banner, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.set_banner(set_banner_request)

    def test_remove_banner_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.DELETE, url_banner, status=204)
            with self.app.app_context():
                self.assertIsNone(admin_controller.remove_banner())

    def test_remove_banner_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.DELETE, url_banner, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.remove_banner()

    # Template tests

    def test_get_templates_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_template, json=templates_response, status=200, content_type='application/json')
            with self.app.app_context():
                response = admin_controller.get_templates()
                self.assertEqual(response, templates_response)

    def test_get_templates_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_template, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.get_templates()

    def test_get_template_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, f"{url_template}/1", json=template_1, status=200, content_type='application/json')
            with self.app.app_context():
                response = admin_controller.get_template("1")
                self.assertEqual(response, template_1)

    def test_get_template_not_found(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, f"{url_template}/1", status=404)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.get_template("1")

    def test_get_template_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, f"{url_template}/1", status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.get_template("1")

    def test_edit_template_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.PUT, url_template, json=template_2, status=200, content_type='application/json')
            with self.app.app_context():
                response = admin_controller.edit_template(template_2)
                self.assertEqual(response, template_2)

    def test_edit_template_bad_request(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.PUT, url_template, status=400)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.edit_template(template_2)

    def test_edit_template_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.PUT, url_template, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.edit_template(template_2)

    def test_delete_template_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.DELETE, f"{url_template}/1", status=204)
            with self.app.app_context():
                self.assertIsNone(admin_controller.delete_template("1"))

    def test_delete_template_bad_request(self):
        """ Bad request happens if the id isn't a number"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.DELETE, f"{url_template}/abc", status=400)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.delete_template("abc")

    def test_delete_template_server_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.DELETE, f"{url_template}/1", status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    admin_controller.delete_template("1")
