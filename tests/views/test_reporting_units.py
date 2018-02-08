import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app


url_search_reporting_units = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/search'


class TestReportingUnits(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    def test_search_reporting_units_get(self):
        response = self.app.get("/reporting-units")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Reporting units".encode(), response.data)

    @requests_mock.mock()
    def test_search_reporting_units(self, mock_request):
        businesses = [{'name': 'test', 'ruref': '123456'}]
        mock_request.get(url_search_reporting_units, json=businesses)

        response = self.app.post("/reporting-units")

        self.assertEqual(response.status_code, 200)
        self.assertIn("test".encode(), response.data)
        self.assertIn("123456".encode(), response.data)

    @requests_mock.mock()
    def test_search_reporting_units_fail(self, mock_request):
        mock_request.post(url_search_reporting_units, status_code=500)

        response = self.app.post("/reporting-units", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)
