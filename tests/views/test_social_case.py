import json
import requests_mock

from config import TestingConfig
from tests.views import ViewTestCase


case_id = "8849c299-5014-4637-bd2b-fc866aeccdf5"
sample_unit_id = "519bb700-1bd9-432d-9db7-d34ea1727415"

get_case_by_id_url = f'{TestingConfig.CASE_URL}/cases/{case_id}?iac=true'
get_sample_by_id_url = f'{TestingConfig.SAMPLE_URL}/samples/{sample_unit_id}/attributes'


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

        response = self.client.get(f'/social/case/{case_id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("LMS0001".encode(), response.data)
        self.assertIn("NV184QG".encode(), response.data)
        self.assertIn("In progress".encode(), response.data)

    @requests_mock.mock()
    def test_get_social_sample_attributes_fail(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, status_code=500)

        response = self.client.get(f'/social/case/{case_id}', follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)
