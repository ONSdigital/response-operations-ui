import unittest

from response_operations_ui import create_app
from response_operations_ui.common.validators import valid_date_for_event
from response_operations_ui.forms import EventDateForm


class TestValidators(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')

    def test_date_can_be_past_for_reference_period_end_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event('ref_period_end', form), True)
            self.assertTrue("invalid_date" not in form.errors)

    def test_date_can_be_past_for_reference_period_start_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event('ref_period_start', form), True)
            self.assertTrue("invalid_date" not in form.errors)

    def test_date_can_be_past_for_employment_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event('employment', form), True)
            self.assertTrue("invalid_date" not in form.errors)

    def test_date_can_not_be_past_for_mps_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event('mps', form), False)
            self.assertTrue("invalid_date" in form.errors)

    def test_date_can_not_be_past_for_go_live_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event('go_live', form), False)
            self.assertTrue("invalid_date" in form.errors)

    def test_date_can_not_be_past_for_reminder_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event('reminder', form), False)
            self.assertTrue("invalid_date" in form.errors)

    @staticmethod
    def _create_form_with_past_date():
        form = EventDateForm()
        form.year.data = "2017"
        form.month.data = "01"
        form.day.data = "01"
        form.hour.data = "01"
        form.minute.data = "00"

        return form
