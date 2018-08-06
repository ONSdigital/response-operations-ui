import json
import mock

import requests_mock

from response_operations_ui import app
from tests.views import ViewTestCase


case_id = "8849c299-5014-4637-bd2b-fc866aeccdf5"
sample_unit_id = "519bb700-1bd9-432d-9db7-d34ea1727415"

get_case_by_id_url = f'{app.config["CASE_URL"]}/cases/{case_id}?iac=true'
get_sample_by_id_url = f'{app.config["SAMPLE_URL"]}/samples/{sample_unit_id}/attributes'


with open('tests/test_data/case/social_case.json') as fp:
    mocked_case_details = json.load(fp)
with open('tests/test_data/sample/sample_attributes.json') as fp:
    mocked_sample_attributes = json.load(fp)


class TestSocialCase(ViewTestCase):

    def setup_data(self):
        pass

    @requests_mock.mock()
    def test_get_social_case(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, json=mocked_sample_attributes)

        response = self.app.get(f'/social/case/{case_id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("LMS0001".encode(), response.data)
        self.assertIn("TS184QG".encode(), response.data)
        self.assertIn("In Progress".encode(), response.data)

    @requests_mock.mock()
    def test_get_social_sample_attributes_fail(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, status_code=500)

        self.app.get(f'/social/case/{case_id}', follow_redirects=True)

        self.assertApiError(get_sample_by_id_url, 500)
