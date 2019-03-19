from response_operations_ui.common.date_restriction_generator import get_date_restriction_text
import unittest

formatted_events = \
    {'return_by': {'day': 'Sunday', 'date': '05 Jan 2020', 'month': '01', 'time': '00:00', 'is_in_future': True},
     'employment': {'day': 'Saturday', 'date': '14 Dec 2019', 'month': '12', 'time': '00:00', 'is_in_future': True},
     'exercise_end': {'day': 'Monday', 'date': '31 Jan 2022', 'month': '01', 'time': '00:00', 'is_in_future': True},
     'mps': {'day': 'Saturday', 'date': '07 Dec 2019', 'month': '12', 'time': '00:00', 'is_in_future': True},
     'go_live': {'day': 'Saturday', 'date': '14 Dec 2019', 'month': '12', 'time': '00:00', 'is_in_future': True},
     'ref_period_start': {'day': 'Monday', 'date': '25 Nov 2019', 'month': '11', 'time': '00:00', 'is_in_future': True},
     'reminder': {'day': 'Wednesday', 'date': '04 Mar 2020', 'month': '03', 'time': '00:00', 'is_in_future': True},
     'reminder2': {'day': 'Thursday', 'date': '05 Mar 2020', 'month': '03', 'time': '07:00', 'is_in_future': True},
     'reminder3': {'day': 'Monday', 'date': '16 Mar 2020', 'month': '03', 'time': '07:00', 'is_in_future': True}}

class TestDateRestrictionGenerator(unittest.TestCase):

    def test_with_no_reminders(self):

        ass

    def test_with_reminder_1(self):


    def test_with_reminder_2(self):


    def test_with_reminder_3(self):
        self.assertTrue(get_date_restriction_text('reminder', formatted_events)
