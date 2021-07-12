import unittest

from response_operations_ui.common.date_restriction_generator import (
    get_date_restriction_text,
)


class TestDateRestrictionGenerator(unittest.TestCase):
    @staticmethod
    def generate_test_ce_events(reminder_one, reminder_two, reminder_three):
        formatted_events = {
            "return_by": {"day": "Sunday", "date": "05 Jan 2020", "month": "01", "time": "00:00", "is_in_future": True},
            "employment": {
                "day": "Saturday",
                "date": "14 Dec 2019",
                "month": "12",
                "time": "00:00",
                "is_in_future": True,
            },
            "exercise_end": {
                "day": "Monday",
                "date": "31 Jan 2022",
                "month": "01",
                "time": "00:00",
                "is_in_future": True,
            },
            "mps": {"day": "Saturday", "date": "07 Dec 2019", "month": "12", "time": "00:00", "is_in_future": True},
            "go_live": {"day": "Saturday", "date": "14 Dec 2019", "month": "12", "time": "00:00", "is_in_future": True},
            "ref_period_start": {
                "day": "Monday",
                "date": "25 Nov 2019",
                "month": "11",
                "time": "00:00",
                "is_in_future": True,
            },
        }
        if reminder_one:
            formatted_events["reminder"] = {
                "day": "Wednesday",
                "date": "04 Mar 2020",
                "month": "03",
                "time": "00:00",
                "is_in_future": True,
            }
        if reminder_two:
            formatted_events["reminder2"] = {
                "day": "Thursday",
                "date": "05 Mar 2020",
                "month": "03",
                "time": "07:00",
                "is_in_future": True,
            }
        if reminder_three:
            formatted_events["reminder3"] = {
                "day": "Monday",
                "date": "16 Mar 2020",
                "month": "03",
                "time": "07:00",
                "is_in_future": True,
            }

        return formatted_events

    def test_with_no_reminders(self):
        date_text = get_date_restriction_text(
            "reminder", self.generate_test_ce_events(reminder_one=False, reminder_two=False, reminder_three=False)
        )
        self.assertTrue("after Go Live" in date_text[0] and "before Exercise end" in date_text[1])

    def test_change_reminder1_with_reminder2(self):
        date_text = get_date_restriction_text(
            "reminder", self.generate_test_ce_events(reminder_one=True, reminder_two=True, reminder_three=False)
        )
        self.assertTrue("after Go Live" in date_text[0] and "before Second Reminder" in date_text[1])

    def test_change_reminder2_with_reminder1_and_reminder3(self):
        date_text = get_date_restriction_text(
            "reminder2", self.generate_test_ce_events(reminder_one=True, reminder_two=False, reminder_three=True)
        )
        self.assertTrue("after First Reminder" in date_text[0] and "before Third Reminder" in date_text[1])

    def test_create_reminder3_with_reminder2(self):
        date_text = get_date_restriction_text(
            "reminder3", self.generate_test_ce_events(reminder_one=False, reminder_two=True, reminder_three=False)
        )
        self.assertTrue("after Second Reminder" in date_text[0] and "before Exercise end" in date_text[1])
