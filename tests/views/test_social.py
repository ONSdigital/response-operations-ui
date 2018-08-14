import json
from urllib.parse import quote_plus

import requests_mock

from config import TestingConfig
from response_operations_ui.views.social.social_case_search import format_address_for_results
from tests.views import ViewTestCase


with open('tests/test_data/case/case_details.json') as f:
    case_details = json.load(f)

CASES_BY_SAMPLE_UNIT_ID_URL = f'{TestingConfig.CASE_URL}/cases/sampleunitids'


def get_postcode_search_url(postcode):
    quote_plus(postcode)
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
        postcode = 'TW9 4ET'

        # Mock getting samples related to postcode
        mock_request.get(get_postcode_search_url(postcode),
                         status_code=200,
                         json=mock_sample_units(postcode))

        # Mock getting cases based on returned samples
        mock_request.get(CASES_BY_SAMPLE_UNIT_ID_URL,
                         status_code=200,
                         json=case_details)

        response = self.client.get(f'/social?query={quote_plus(postcode)}')

        self.assertEqual(response.status_code, 200)

        self.assertIn(f'1 result found for {postcode}', str(response.data))

    @requests_mock.mock()
    def test_postcode_not_found(self, mock_request):
        postcode = 'LE18 FML'

        mock_request.get(get_postcode_search_url(postcode), status_code=404)

        response = self.client.get(f'/social?query={quote_plus(postcode)}')

        self.assertEqual(response.status_code, 200)
        self.assertIn(f'0 results found for {postcode}', str(response.data))

    def test_format_result_address_all_fields_present(self):
        sample_unit_attributes = {
            'Prem1': '1',
            'Prem2': '2',
            'Prem3': '3',
            'Prem4': '4',
            'District': 'district',
            'PostTown': 'posttown'
        }

        formatted_address = format_address_for_results(sample_unit_attributes)
        self.assertEqual('1, 2, 3, 4, district, posttown',
                         formatted_address,
                         'Formatted address with all fields does not match requirement')

    def test_format_result_address_missing_fields(self):
        sample_unit_attributes = {
            'Prem1': '1',
            'PostTown': 'posttown'
        }

        formatted_address = format_address_for_results(sample_unit_attributes)
        self.assertEqual('1, posttown',
                         formatted_address,
                         'Formatted address with missing fields does not match requirement')
