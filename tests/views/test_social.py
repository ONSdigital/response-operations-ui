import unittest
import requests_mock
import json
from response_operations_ui import create_app
from config import TestingConfig
from tests.views import ViewTestCase

app = create_app('TestingConfig')
client = app.test_client()

with open('tests/test_data/case/case_details.json') as f:
    case_details = json.load(f)

CASE_SAMPLES_URL = f'{TestingConfig.CASE_URL}/cases/sampleunitids'


def postcode_url(postcode):
    postcode = postcode.replace(' ', '+')
    return f'{TestingConfig.SAMPLE_URL}/samples/sampleunits?postcode={postcode}'


def mock_sample_units(postcode):
    with open('tests/test_data/sample/sample_units.json') as f:
        sample_units = json.load(f)
        sample_units[0]['sampleAttributes']['attributes']['Postcode'] = postcode
    return sample_units


class TestSocial(ViewTestCase):

    def setup_data(self):
        pass

    @requests_mock.mock()
    def test_valid_postcode(self, mock_request):
        pc = 'TW9 4ET'

        # Mock getting samples related to postcode
        mock_request.get(postcode_url(pc), status_code=200, json=mock_sample_units(pc))

        # Mock getting cases based on returned samples
        mock_request.get(CASE_SAMPLES_URL, status_code=200, json=case_details)

        response = client.post("/social", data={'query': pc})

        self.assertEqual(response.status_code, 200)

        self.assertIn(f'1 result found for {pc}', str(response.data))

    @requests_mock.mock()
    def test_invalid_postcode(self, mock_request):
        pc = 'LE18 FML'

        mock_request.get(postcode_url(pc), status_code=404)

        response = client.post("/social", data={'query': pc})

        self.assertEqual(response.status_code, 200)
        self.assertIn(f'0 results found for {pc}', str(response.data))

        # A blank postcode cannot be entered due to text validation in place on the UI
        # If a blank post code is somehow entered, it is deemed invalid and will bear similar results to this test case
