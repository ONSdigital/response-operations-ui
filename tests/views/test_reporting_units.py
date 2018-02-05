import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app


url_get_reporting_unit = f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/50012345678'
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
