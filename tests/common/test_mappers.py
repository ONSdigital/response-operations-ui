import unittest

from response_operations_ui.common.mappers import map_social_case_event, get_social_status_from_event


class TestMappers(unittest.TestCase):

    def test_map_valid_social_case_event(self):
        mapped_event = map_social_case_event('PRIVACY_DATA_CONFIDENTIALITY_CONCERNS')
        self.assertEqual(mapped_event, '411 Privacy Concerns/Data security/confidentiality concerns')

    def test_map_invalid_social_case_event_is_returned(self):
        mapped_event = map_social_case_event('NOT_A_SOCIAL_CASE_EVENT')
        self.assertEqual(mapped_event, 'NOT_A_SOCIAL_CASE_EVENT')

    def test_map_invalid_social_cases_event_default_to_None(self):
        mapped_event = map_social_case_event('NOT_A_SOCIAL_CASE_EVENT', default_to_none=True)
        self.assertIsNone(mapped_event)

    def test_map_social_event_to_status(self):
        mapped_status = get_social_status_from_event('PRIVACY_DATA_CONFIDENTIALITY_CONCERNS')
        self.assertEqual(mapped_status, 'REFUSAL')

    def test_map_invalid_social_event_to_status(self):
        mapped_status = get_social_status_from_event('NOT_A_SOCIAL_CASE_EVENT')
        self.assertIsNone(mapped_status)
