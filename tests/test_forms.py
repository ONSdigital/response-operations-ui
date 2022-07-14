import unittest

from response_operations_ui import create_app
from response_operations_ui.forms import CreateAccountWithPermissionsForm


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
                self.assertEquals(len(form.errors), 0)
