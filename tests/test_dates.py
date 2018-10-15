import unittest
from datetime import datetime, timezone, date
from unittest.mock import patch

from response_operations_ui.common.dates import get_formatted_date, localise_datetime


class TestDates(unittest.TestCase):

    def test_get_formatted_date_today_date(self):
        with patch('response_operations_ui.common.dates.date') as mock_date:
            mock_date.today.return_value = date(2018, 6, 12)
            today_example_date = get_formatted_date('2018-06-12 14:15:12')
            self.assertEqual(today_example_date, 'Today at 15:15')

    def test_get_formatted_date_yesterday_date(self):
        with patch('response_operations_ui.common.dates.date') as mock_date:
            mock_date.today.return_value = date(2018, 2, 12)
            yesterday_example_date = get_formatted_date('2018-02-11 14:15:12')
            self.assertEqual(yesterday_example_date, 'Yesterday at 14:15')

    def test_get_formatted_date_full_dates(self):
        self.assertEqual(get_formatted_date('2000-01-01 00:00:00'), '01 Jan 2000 00:00')
        self.assertEqual(get_formatted_date('2020-01-01 00:00:00'), '01 Jan 2020 00:00')
        self.assertEqual(get_formatted_date('3000-01-01 00:00:00'), '01 Jan 3000 00:00')
        self.assertEqual(get_formatted_date('1999-12-31 23:59:59'), '31 Dec 1999 23:59')
        self.assertEqual(get_formatted_date('2000-01-01 00:00:00'), '01 Jan 2000 00:00')

    def test_get_formatted_date_29th_feb(self):
        # Check formatting on a valid leap day
        self.assertEqual(get_formatted_date('2016-02-29 01:01:01'), '29 Feb 2016 01:01')
        # Should not format a leap day on a non leap year
        self.assertEqual(get_formatted_date('2018-02-29 01:01:01'), '2018-02-29 01:01:01')

    def test_get_formatted_date_returns_malformed_dates(self):
        # Strings not in the correct format or invalid dates should be returned as given and a exception logged
        self.assertEqual(get_formatted_date(''), '')
        self.assertEqual(get_formatted_date('1999-12-32 23:59:59'), '1999-12-32 23:59:59')

    def test_convert_to_bst_from_utc_during_bst(self):
        # 13th Jun 2018 at 14.12 should return 13th Jun 2018 at 15.12
        datetime_parsed = datetime(2018, 6, 13, 14, 12, 0, tzinfo=timezone.utc)
        returned_datetime = localise_datetime(datetime_parsed)
        # Check date returned is in BST format
        self.assertEqual(datetime.strftime(returned_datetime, '%Y-%m-%d %H:%M:%S'), '2018-06-13 15:12:00')

    def test_convert_to_bst_from_utc_during_gmt(self):
        # 13th Feb 2018 at 14.12 should return 13th Feb 2018 at 14.12
        datetime_parsed = datetime(2018, 2, 13, 14, 12, 0, tzinfo=timezone.utc)
        returned_datetime = localise_datetime(datetime_parsed)
        # Check date returned is in BST format
        self.assertEqual(datetime.strftime(returned_datetime, '%Y-%m-%d %H:%M:%S'), '2018-02-13 14:12:00')
