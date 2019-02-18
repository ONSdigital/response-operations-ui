import unittest

from response_operations_ui.common.respondent_utils import status_enum_to_string, status_enum_to_class, get_controller_args_from_request, filter_respondents


class TestRespondentUtils(unittest.TestCase):
    def test_status_enum_to_string_green(self):
        valid_key_outputs = {
            'ACTIVE': status_enum_to_string('ACTIVE'),
            'CREATED': status_enum_to_string('CREATED'),
            'SUSPENDED': status_enum_to_string('SUSPENDED'),
            'LOCKED': status_enum_to_string('LOCKED')
        }

        for k, v in valid_key_outputs:
            self.assertIsInstance(v, str, f'Input {k} returned a non-string object (type received {type(v)})')
            self.Greater(len(v), 0, f'Input {k} returned a zero-length string.')

    def test_status_enum_to_string_red(self):
        invalid_key_outputs = status_enum_to_string('INVALIDKEY')
        self.assertEqual(invalid_key_outputs, None)
    
    def test_status_enum_to_class_green(self):
        valid_key_outputs = {
            'ACTIVE': status_enum_to_class('ACTIVE'),
            'CREATED': status_enum_to_class('CREATED'),
            'SUSPENDED': status_enum_to_class('SUSPENDED'),
            'LOCKED': status_enum_to_class('LOCKED')
        }

        for k, v in valid_key_outputs:
            self.assertIsInstance(v, str, f'Input {k} returned a non-string object (type received {type(v)})')
            self.Greater(len(v), 0, f'Input {k} returned a zero-length string.')

    def test_status_enum_to_class_red(self):
        invalid_key_outputs = status_enum_to_class('INVALIDKEY')
        self.assertEqual(invalid_key_outputs, None)

    def test_get_controller_args_from_request_red(self):
        args = get_controller_args_from_request()
        self.assertFalse(args)
    
    def test_get_controller_args_from_request_green(self):
        request = {
            'values': {
                'email_address': 'email@email.com',
                'first_name': 'Bob',
                'last_name': 'Cheese'
            } 
        }
        expectation = request.values
        args = get_controller_args_from_request(request)
        self.assertDictEqual(args, expectation)

    def filter_respondents_

