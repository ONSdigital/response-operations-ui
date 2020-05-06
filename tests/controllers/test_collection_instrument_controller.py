import unittest

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers.collection_instrument_controllers import \
    link_collection_instrument_to_survey
from response_operations_ui.exceptions.exceptions import ApiError

test_survey_uuid = 'b2dd0330-09c7-408f-a7c4-fa1a2bb3bfdd'
test_eq_id = 'vacancies'
test_form_type = '0001'

ci_link_url = f'{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2/' \
              f'upload?survey_id={test_survey_uuid}' \
              f'&classifiers=%7B%22form_type%22%3A%22{test_form_type}%22%2C%22eq_id%22%3A%22{test_eq_id}%22%7D'


class TestCollectionInstrumentController(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    def test_link_collection_instrument_to_survey_success(self):
        """Tests on success (200) nothing is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_url, status=200)
            with self.app.app_context():
                self.assertIsNone(link_collection_instrument_to_survey(test_survey_uuid, test_eq_id, test_form_type))

    def test_link_collection_instrument_to_survey_unauthorised(self):
        """Tests on unauthorised (403) an APIError is raised"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_url, status=403)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    link_collection_instrument_to_survey(test_survey_uuid, test_eq_id, test_form_type)
