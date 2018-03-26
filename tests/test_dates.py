from datetime import datetime
import unittest

from response_operations_ui.common.dates import get_formatted_date


class TestDates(unittest.TestCase):

    def test_get_formatted_date_today(self):
        today_formatted_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(get_formatted_date(today_formatted_string),
                         f'Today at {today_formatted_string[11:16]}')

    def test_get_formatted_date_yesterday(self):
        today = datetime.now()
        yesterday_formatted_string = today.replace(day=today.day - 1).strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(get_formatted_date(yesterday_formatted_string),
                         f'Yesterday at {yesterday_formatted_string[11:16]}')

    def test_get_formatted_date_full_dates(self):
        self.assertEqual(get_formatted_date('2000-01-01 00:00:00'), '01 Jan 2000 00:00')
        self.assertEqual(get_formatted_date('1999-12-31 23:59:59'), '31 Dec 1999 23:59')

        self.assertEqual(get_formatted_date('00:00:00 2000-01-01', string_format='%H:%M:%S %Y-%m-%d'),
                         '01 Jan 2000 00:00')

    def test_get_formatted_date_returns_malformed_dates(self):
        # Strings not in the correct format should be returned as given and a exception logged
        self.assertEqual(get_formatted_date(''), '')
