import unittest

from response_operations_ui import create_app
from response_operations_ui.forms import CreateAccountWithPermissionsForm, SetAccountPasswordForm


class TestForms(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

    def test_only_ons_email_address_valid(self):
        with self.app.app_context():
            form = CreateAccountWithPermissionsForm()
            form.first_name.data = "First"
            form.last_name.data = "Last"
            form.email.data = "some.one@fail.com"
            result = form.validate()
            self.assertFalse(result)
            self.assertEqual(len(form.errors.get("email")), 1)  # Check there is only 1 error
            self.assertEqual(form.errors.get("email")[0], "Not a valid ONS email address")

            correct_emails = ["some.one@ons.gov.uk", "some.one@ext.ons.gov.uk", "some.one@ons.fake"]
            for email in correct_emails:
                form.email.data = email
                result = form.validate()
                self.assertTrue(result)
                self.assertEqual(len(form.errors), 0)
                
    def test_valid_password_for_activation_and_reset(self):
        with self.app.app_context():
            form = SetAccountPasswordForm()
            form.password.data = "Abcde123Edcba!"
            form.password_confirm.data = "Abcde123Edcba!"
            result = form.validate()
            self.assertTrue(result)
            self.assertTrue(len(form.errors) == 0)
            
    def test_nonvalid_password_for_activation_and_reset(self):
        with self.app.app_context():
            form = SetAccountPasswordForm()
            password_too_short = "Abcde123!"
            password_missing_numbers = "AbcdeEdcba!"
            password_missing_letters = "12345678910!"
            password_missing_special_char = "Abcde123Edcba"
            password_too_long = r"Abcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcde123Edcba" \
                                r"Abcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcde123EdcbaAbcd2!"

            incorrect_passwords = [password_too_short, password_missing_letters, password_missing_numbers, 
                                    password_too_long, password_missing_special_char]
            
            for password in incorrect_passwords:
                form.password.data = password
                form.password_confirm.data = password
                result = form.validate()
                self.assertFalse(result)
                self.assertTrue(form.errors.get("password")[0], "Your password doesn't meet the requirements")
            
