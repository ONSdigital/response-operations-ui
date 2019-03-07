import unittest

from response_operations_ui.common.respondent_utils import status_enum_to_string, \
    status_enum_to_class, get_controller_args_from_request, filter_respondents


valid_statuses = [
    'ACTIVE',
    'CREATED',
    'SUSPENDED',
    'LOCKED'
]


class TestRespondentUtils(unittest.TestCase):
    """
    Tests for enum methods test the output works, but _not_ what it is.  This is because otherwise the test is just
    a reimplementation of the method.
    """
    def test_status_enum_to_string_returns_a_nonzero_length_string_for_all_valid_statuses(self):
        valid_key_outputs = {}

        for status in valid_statuses:
            valid_key_outputs[status] = status_enum_to_string(status)

        for k, v in valid_key_outputs.items():
            self.assertIsInstance(v, str, f'Input {k} returned a non-string object (type received {type(v)})')
            self.assertGreater(len(v), 0, f'Input {k} returned a zero-length string.')

    def test_status_enum_to_string_returns_none_for_invalid_enum_key(self):
        invalid_key_outputs = status_enum_to_string('INVALIDKEY')
        self.assertEqual(invalid_key_outputs, None)

    def returns_a_nonzero_length_string_for_all_valid_statuses(self):
        valid_key_outputs = {}

        for status in valid_statuses:
            valid_key_outputs[status] = status_enum_to_class(status)

        for k, v in valid_key_outputs:
            self.assertIsInstance(v, str, f'Input {k} returned a non-string object (type received {type(v)})')
            self.assertGreater(len(v), 0, f'Input {k} returned a zero-length string.')

    def test_status_enum_to_class_returns_none_for_invalid_enum_key(self):
        invalid_key_outputs = status_enum_to_class('INVALIDKEY')
        self.assertEqual(invalid_key_outputs, None)

    def test_get_controller_args_from_request_returns_false_if_sent_request_object_without_expected_values(self):
        args = get_controller_args_from_request({})
        self.assertFalse(args)

    def test_get_controller_args_from_request_returns_args_if_passed_valid_request(self):
        request = {
            'values': {
                'email_address': 'email@email.com',
                'first_name': 'Bob',
                'last_name': 'Cheese',
                'page': 5
            }
        }
        expectation = request['values']
        args = get_controller_args_from_request(request)
        self.assertDictEqual(args, expectation)

    def test_get_controller_args_from_request_returns_only_the_args_we_need(self):
        request = {
            'values': {
                'email_address': 'email@email.com',
                'first_name': 'Bob',
                'last_name': 'Cheese',
                'spurious_value': 'value'
            }
        }
        args = get_controller_args_from_request(request)
        self.assertIsNone(args.get('spurious_value'))

    def test_filter_respondents_returns_empty_list_if_given_no_results(self):
        self.assertEqual(filter_respondents([]), [])

    def test_filter_respondents_returns_list_of_correct_length_when_passed_list(self):
        correct_item = [{
            'id': 0,
            'firstName': '',
            'lastName': '',
            'emailAddress': '',
            'status': 'ACTIVE',
            'status_class': 'ACTIVE'
        }]
        test_lengths = [0, 5, 48]

        for length in test_lengths:
            output = filter_respondents(correct_item * length)
            self.assertEqual(length, len(output))

    def test_filter_respondents_ignores_extra_values(self):
        list_with_spurious_item = [{
            'id': 1,
            'firstName': '',
            'lastName': '',
            'emailAddress': '',
            'status': 'ACTIVE',
            'something_we_dont_need': ''
        }]
        output = filter_respondents(list_with_spurious_item)
        self.assertEqual(output[0].get('something_we_dont_need'), None)

    def test_filter_respondents_assembles_href(self):
        correct_item = [{
            'id': 515,
            'firstName': '',
            'lastName': '',
            'emailAddress': '',
            'status': 'ACTIVE',
            'status_class': 'ACTIVE'
        }]
        output = filter_respondents(correct_item)
        self.assertEqual(output[0]['href'], '/respondent-details/515')

    def test_filter_respondents_assembles_name(self):
        correct_item = [{
            'id': 515,
            'firstName': 'Bob',
            'lastName': 'Martin',
            'emailAddress': '',
            'status': 'ACTIVE',
            'status_class': 'ACTIVE'
        }]
        output = filter_respondents(correct_item)
        self.assertEqual(output[0]['name'], 'Bob Martin')

    def test_filter_respondents_includes_email_address(self):
        correct_item = [{
            'id': 515,
            'firstName': '',
            'lastName': '',
            'emailAddress': 'abc@cdefg.com',
            'status': 'ACTIVE',
            'status_class': 'ACTIVE'
        }]
        output = filter_respondents(correct_item)
        self.assertEqual(output[0]['email'], 'abc@cdefg.com')
