import json

import requests_mock

from config import TestingConfig
from tests.views import ViewTestCase

case_id = "8849c299-5014-4637-bd2b-fc866aeccdf5"
sample_unit_id = "519bb700-1bd9-432d-9db7-d34ea1727415"
collection_exercise_id = "6553d121-df61-4b3a-8f43-e0726666b8cc"
ru_ref = "LMS0001"

get_case_by_id_url = f'{TestingConfig.CASE_URL}/cases/{case_id}?iac=true'
iac_url = f'{TestingConfig.CASE_URL}/cases/{case_id}/iac'
get_sample_by_id_url = f'{TestingConfig.SAMPLE_URL}/samples/{sample_unit_id}/attributes'
get_case_events_by_case_id = f'{TestingConfig.CASE_URL}/cases/{case_id}/events'
url_get_available_case_group_statuses_direct = f'{TestingConfig.CASE_URL}/casegroups/transitions' \
                                               f'/{collection_exercise_id}/{ru_ref}'
url_update_case_group_status = f'{TestingConfig.CASE_URL}/casegroups/transitions/{collection_exercise_id}/{ru_ref}'

with open('tests/test_data/case/social_case.json') as fp:
    mocked_case_details = json.load(fp)
with open('tests/test_data/case/iacs.json') as fp:
    mocked_iacs = json.load(fp)
with open('tests/test_data/case/iac.json') as fp:
    mocked_iac = json.load(fp)
with open('tests/test_data/sample/sample_attributes.json') as fp:
    mocked_sample_attributes = json.load(fp)
with open('tests/test_data/case/social_case_events.json') as fp:
    mocked_case_events = json.load(fp)
with open('tests/test_data/case/case_group_statuses.json') as fp:
    case_group_statuses = json.load(fp)


class TestSocialCase(ViewTestCase):

    def setup_data(self):
        pass

    @requests_mock.mock()
    def test_get_social_case(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, json=mocked_sample_attributes)
        mock_request.get(get_case_events_by_case_id, json=mocked_case_events)
        mock_request.get(iac_url, json=mocked_iacs)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)

        response = self.client.get(f'/social/case/{case_id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("LMS0001".encode(), response.data)
        self.assertIn("NV184QG".encode(), response.data)
        self.assertIn("In progress".encode(), response.data)

    @requests_mock.mock()
    def test_get_social_sample_attributes_fail(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, status_code=500)
        mock_request.get(iac_url, json=mocked_iacs)

        response = self.client.get(f'/social/case/{case_id}', follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_generate_iac(self, mock_request):
        post_data = {"case_id": case_id}

        mock_request.post(iac_url, json=mocked_iac)
        mock_request.get(iac_url, json=mocked_iacs)
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, json=mocked_sample_attributes)
        mock_request.get(get_case_events_by_case_id, json=mocked_case_events)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)

        response = self.client.post(f'/social/iac', follow_redirects=True, data=post_data)

        self.assertIn("k7j6n7pffg8g".encode(), response.data)
        self.assertIn("16 unique".encode(), response.data)

    @requests_mock.mock()
    def test_update_case_status_view(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.get(get_sample_by_id_url, json=mocked_sample_attributes)
        mock_request.get(get_case_events_by_case_id, json=mocked_case_events)
        mock_request.get(url_get_available_case_group_statuses_direct, json=case_group_statuses)

        response = self.client.get(f'/social/case/{case_id}/change-response-status', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("In progress".encode(), response.data)

    @requests_mock.mock()
    def test_change_response_status(self, mock_request):
        mock_request.get(get_case_by_id_url, json=mocked_case_details)
        mock_request.put(url_update_case_group_status)

        response = self.client.post(f'/social/case/{case_id}/change-response-status?status_updated=True&updated_'
                                    f'status=PRIVACY_DATA_CONFIDENTIALITY_CONCERNS',
                                    data={'event': 'LEGITIMACY_CONCERNS'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('http://localhost/social/case/8849c299-5014-4637-bd2b-fc866aeccdf5?'
                      'status_updated=True&updated_status=LEGITIMACY_CONCERNS', response.location)
