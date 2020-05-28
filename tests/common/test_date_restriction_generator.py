import unittest
from response_operations_ui.common.date_restriction_generator import get_date_restriction_text


class TestDateRestrictionGenerator(unittest.TestCase):
    restriction_texts = {
        "nudge_email_restriction_text": ["Maximum of five nudge email allowed",
                                         "Must be after Go Live Tuesday 02 Jun 2020 07:00",
                                         "Must be before Return by Tuesday 30 Jun 2020 07:00"],
        "reminder_email_restriction_text": ["Must be after Go Live Tuesday 02 Jun 2020 07:00",
                                            "Must be before Exercise end Tuesday 30 Jun 2020 07:00"],
        "exercise_end_restriction_text": ["Must be after Return by Tuesday 30 Jun 2020 07:00"],
        "return_by_restriction_text": ["Must be after Go Live Tuesday 02 Jun 2020 07:00",
                                       "Must be before Exercise end Tuesday 30 Jun 2020 07:00"],
        "go_live_restriction_text": ["Must be after MPS Monday 01 Jun 2020 07:00",
                                     "Must be before Return by Tuesday 30 Jun 2020 07:00"],
        "mps_restriction_text": ["Must be before Go Live Tuesday 02 Jun 2020 07:00"]
    }

    events = {
        'go_live': {
            'day': 'Tuesday',
            'date': '02 Jun',
            'time': '2020 07:00'
        },
        'return_by': {
            'day': 'Tuesday',
            'date': '30 Jun',
            'time': '2020 07:00'
        },
        'exercise_end': {
            'day': 'Tuesday',
            'date': '30 Jun',
            'time': '2020 07:00'
        },
        'mps': {
            'day': 'Monday',
            'date': '01 Jun',
            'time': '2020 07:00'
        }
    }

    def test_nudge_email_0_date_restriction(self):
        self.assertEqual(get_date_restriction_text('nudge_email_0', self.events),
                         self.restriction_texts['nudge_email_restriction_text'])

    def test_nudge_email_1_date_restriction(self):
        self.assertEqual(get_date_restriction_text('nudge_email_1', self.events),
                         self.restriction_texts['nudge_email_restriction_text'])

    def test_nudge_email_2_date_restriction(self):
        self.assertEqual(get_date_restriction_text('nudge_email_2', self.events),
                         self.restriction_texts['nudge_email_restriction_text'])

    def test_nudge_email_3_date_restriction(self):
        self.assertEqual(get_date_restriction_text('nudge_email_3', self.events),
                         self.restriction_texts['nudge_email_restriction_text'])

    def test_nudge_email_4_date_restriction(self):
        self.assertEqual(get_date_restriction_text('nudge_email_4', self.events),
                         self.restriction_texts['nudge_email_restriction_text'])

    def test_reminder_date_restriction(self):
        self.assertEqual(get_date_restriction_text('reminder', self.events),
                         self.restriction_texts['reminder_email_restriction_text'])

    def test_exercise_end_date_restriction(self):
        self.assertEqual(get_date_restriction_text('exercise_end', self.events),
                         self.restriction_texts['exercise_end_restriction_text'])

    def test_return_by_date_restriction(self):
        self.assertEqual(get_date_restriction_text('return_by', self.events),
                         self.restriction_texts['return_by_restriction_text'])

    def test_go_live_date_restriction(self):
        self.assertEqual(get_date_restriction_text('go_live', self.events),
                         self.restriction_texts['go_live_restriction_text'])

    def test_mps_date_restriction(self):
        self.assertEqual(get_date_restriction_text('mps', self.events),
                         self.restriction_texts['mps_restriction_text'])
