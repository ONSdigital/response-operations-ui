import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app


url_get_reporting_unit = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/50012345678'
url_search_reporting_units = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/search'
with open('tests/test_data/reporting_units/reporting_unit.json') as json_data:
    reporting_unit = json.load(json_data)


class TestReportingUnits(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    @requests_mock.mock()
    def test_get_reporting_unit(self, mock_request):
        mock_request.get(url_get_reporting_unit, json=reporting_unit)

        response = self.app.get("/reporting-units/50012345678")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)
        self.assertIn("BLOCKS".encode(), response.data)
        self.assertIn("BRICKS".encode(), response.data)
        self.assertIn("GB".encode(), response.data)
        self.assertIn("YY".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_fail(self, mock_request):
        mock_request.get(url_get_reporting_unit, status_code=500)

        response = self.app.get("/reporting-units/50012345678", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

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
        mock_request.get(url_search_reporting_units, status_code=500)

        response = self.app.post("/reporting-units", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)
