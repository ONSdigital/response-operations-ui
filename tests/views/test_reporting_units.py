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
        self.case_group_status = {
            "ru_ref": "19000001",
            "trading_as": "Company Name",
            "survey_id": "123",
            "short_name": "MYSURVEY",
            "current_status": "NOTSTARTED",
            "available_statuses": {
                "UPLOADED": "COMPLETE",
                "COMPLETED_BY_PHONE": "COMPLETEDBYPHONE"
            }
        }

    @requests_mock.mock()
    def test_get_reporting_unit(self, mock_request):
        mock_request.get(url_get_reporting_unit, json=reporting_unit)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201802/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201802/50012345678',
                         json=self.case_group_status)

        response = self.app.get("/reporting-units/50012345678")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bolts and Ratchets Ltd".encode(), response.data)
        self.assertIn("50012345678".encode(), response.data)
        self.assertIn("BLOCKS".encode(), response.data)
        self.assertIn("BRICKS".encode(), response.data)
        self.assertIn("GB".encode(), response.data)
        self.assertIn("NI".encode(), response.data)
        self.assertIn("Jacky Turner".encode(), response.data)
        self.assertIn("Enabled".encode(), response.data)
        self.assertIn("Active".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_when_changed_status_shows_new_status(self, mock_request):
        mock_request.get(url_get_reporting_unit, json=reporting_unit)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201802/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201802/50012345678',
                         json=self.case_group_status)

        response = self.app.get("/reporting-units/50012345678?survey=BRICKS&period=201801")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Response status for 074 BRICKS period 201801 changed to Completed".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_shows_change_link_when_no_available_statuses_hides_change_link(self, mock_request):
        mock_request.get(url_get_reporting_unit, json=reporting_unit)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201802/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201802/50012345678',
                         json=self.case_group_status)

        response = self.app.get("/reporting-units/50012345678?survey=BRICKS&period=201801")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Change</a>".encode(), response.data)

    @requests_mock.mock()
    def test_get_reporting_unit_hides_change_link_when_no_available_statuses(self, mock_request):
        mock_request.get(url_get_reporting_unit, json=reporting_unit)
        collex = {'available_statuses': []}
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201801/50012345678', json=collex)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201802/50012345678', json=collex)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201801/50012345678', json=collex)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201802/50012345678', json=collex)

        response = self.app.get("/reporting-units/50012345678?survey=BRICKS&period=201801")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Change</a>".encode(), response.data)

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
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/search', json=businesses)

        response = self.app.post("/reporting-units")

        self.assertEqual(response.status_code, 200)
        self.assertIn("test".encode(), response.data)
        self.assertIn("123456".encode(), response.data)

    @requests_mock.mock()
    def test_search_reporting_units_fail(self, mock_request):
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/reporting-unit/search', status_code=500)

        response = self.app.post("/reporting-units", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)
