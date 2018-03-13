import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app

respondent_party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"
backstage_api_url = app.config["BACKSTAGE_API_URL"]

url_get_reporting_unit = f'{backstage_api_url}/v1/reporting-unit/50012345678'
url_search_reporting_units = f'{backstage_api_url}/v1/reporting-unit/search'
url_get_contact_details = f'{backstage_api_url}/v1/party/party-details?respondent_party_id={respondent_party_id}'
url_edit_contact_details = f'{backstage_api_url}/v1/party/update-respondent-details/{respondent_party_id}'
url_generate_new_code = f'{backstage_api_url}/v1/reporting-unit/iac/ce_id/ru_ref'
with open('tests/test_data/reporting_units/reporting_unit.json') as json_data:
    reporting_unit = json.load(json_data)
with open('tests/test_data/reporting_units/respondent.json') as json_data:
    respondent = json.load(json_data)
with open('tests/test_data/reporting_units/edited_reporting_unit.json') as json_data:
    edited_reporting_unit = json.load(json_data)
with open('tests/test_data/case/case.json') as json_data:
    case = json.load(json_data)


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

    @requests_mock.mock()
    def test_get_contact_details(self, mock_request):
        mock_request.get(url_get_contact_details, json=respondent)

        response = self.app.get(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Jacky".encode(), response.data)
        self.assertIn("Turner".encode(), response.data)
        self.assertIn("7971161859".encode(), response.data)

    @requests_mock.mock()
    def test_get_contact_details_fail(self, mock_request):
        mock_request.get(url_get_contact_details, status_code=500)

        response = self.app.get(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161867'}
        mock_request.put(url_edit_contact_details)
        mock_request.get(url_get_reporting_unit + '?edit_details=True')
        mock_request.get(url_get_reporting_unit, json=edited_reporting_unit)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BLOCKS/201802/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201801/50012345678',
                         json=self.case_group_status)
        mock_request.get(f'{app.config["BACKSTAGE_API_URL"]}/v1/case/status/BRICKS/201802/50012345678',
                         json=self.case_group_status)

        response = self.app.post(f"/reporting-units/50012345678/edit-contact-details/{respondent_party_id}",
                                 data=changed_details, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Tom'.encode(), response.data)
        self.assertIn('Smith'.encode(), response.data)
        self.assertIn('7971161867'.encode(), response.data)

    @requests_mock.mock()
    def test_edit_contact_details_fail(self, mock_request):
        changed_details = {
            "first_name": 'Tom',
            "last_name": 'Smith',
            "email": 'Jacky.Turner@email.com',
            "telephone": '7971161867'}
        mock_request.put(url_edit_contact_details, status_code=500)

        response = self.app.post(
            "/reporting-units/50012345678/edit-contact-details/cd592e0f-8d07-407b-b75d-e01fbdae8233",
            data=changed_details, follow_redirects=True)

        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code(self, mock_request):
        mock_request.post(url_generate_new_code, json=case)

        response = self.app.get("/reporting-units/ru_ref/ce_id/new_enrolment_code", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("jkbvyklkwj88".encode(), response.data)

    @requests_mock.mock()
    def test_reporting_unit_generate_new_code_fail(self, mock_request):
        mock_request.post(url_generate_new_code, status_code=500)

        response = self.app.get("/reporting-units/ru_ref/ce_id/new_enrolment_code", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)
