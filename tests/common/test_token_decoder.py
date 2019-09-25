import unittest
import time

from response_operations_ui.common.token_decoder import generate_email_token, decode_email_token
from werkzeug.exceptions import InternalServerError
from itsdangerous import SignatureExpired, BadSignature
from response_operations_ui import create_app


class TestTokenDecoder(unittest.TestCase):
    """
    Tests that email token generation/decoding works as expected
    """
    def setUp(self):
        self.app = create_app('TestingConfig')

    def test_generating_and_decoding_email_token(self):
        with self.app.app_context():
            try:
                email_token = generate_email_token("test@ons.gov")
            except InternalServerError:
                self.fail('Exception raised in generating email token')

            email = decode_email_token(email_token)
            self.assertTrue(email == "test@ons.gov", 'Email not successfully decoded from token')

            time.sleep(2)

            with(self.assertRaises(SignatureExpired)):
                decode_email_token(email_token, 1)

            with(self.assertRaises(BadSignature)):
                decode_email_token("absoluterubbish")
