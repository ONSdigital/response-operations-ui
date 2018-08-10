import unittest
import requests_mock
import json
from response_operations_ui import app

with open('tests/test_data/case/case_details.json') as f:
    case_details = json.load(f)

CASE_SAMPLES_URL = f'{app.config["CASE_URL"]}/cases/sampleunitids'


def postcode_url(postcode):
    postcode = postcode.replace(' ', '+')
    return f'{app.config["SAMPLE_URL"]}/samples/sampleunits?postcode={postcode}'


def mock_sample_units(postcode):
    with open('tests/test_data/sample/sample_units.json') as f:
        sample_units = json.load(f)
        sample_units[0]['sampleAttributes']['attributes']['Postcode'] = postcode
    return sample_units


class TestSocial(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @requests_mock.mock()
    def testValidPostcode(self, mock_request):
        pc = 'TW9 4ET'

        # Mock getting samples related to postcode
        mock_request.get(postcode_url(pc), status_code=201, json=mock_sample_units(pc))

        # Mock getting cases based on returned samples
        mock_request.get(CASE_SAMPLES_URL, status_code=201, json=case_details)

        response = self.app.post("/social", data={'query': pc})

        self.assertEqual(response.status_code, 200)

        self.assertIn(f'1 result found for {pc}', str(response.data))

    @requests_mock.mock()
    def testInvalidPostcode(self, mock_request):
        pc = 'LE18 FML'

        mock_request.get(postcode_url(pc), status_code=404, json=mock_sample_units(pc))

        # Mock getting cases based on returned samples
        mock_request.get(CASE_SAMPLES_URL, status_code=404, json=case_details)

        response = self.app.post("/social", data={'query': pc})

        self.assertEqual(response.status_code, 200)
        self.assertIn(f'0 results found for {pc}', str(response.data))

        # A blank postcode cannot be entered due to text validation in place on the UI
        # If a blank post code is somehow entered, it is deemed invalid and will bear similar results to this test case
