import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from response_operations_ui.common.dates import (
    format_datetime_to_string,
    get_formatted_date,
    localise_datetime,
)


class TestDates(unittest.TestCase):
    def test_get_formatted_date_today_date(self):
        with patch("response_operations_ui.common.dates.date") as mock_date:
            mock_date.today.return_value = date(2018, 6, 12)
            today_example_date = get_formatted_date("2018-06-12 14:15:12")
            self.assertEqual(today_example_date, "Today at 15:15")

    def test_get_formatted_date_yesterday_date(self):
        with patch("response_operations_ui.common.dates.date") as mock_date:
            mock_date.today.return_value = date(2018, 2, 12)
            yesterday_example_date = get_formatted_date("2018-02-11 14:15:12")
            self.assertEqual(yesterday_example_date, "Yesterday at 14:15")

    def test_get_formatted_date_full_dates(self):
        self.assertEqual(get_formatted_date("2000-01-01 00:00:00"), "01 Jan 2000 00:00")
        self.assertEqual(get_formatted_date("3000-01-01 00:00:00"), "01 Jan 3000 00:00")
        self.assertEqual(get_formatted_date("1999-12-31 23:59:59"), "31 Dec 1999 23:59")

    def test_get_formatted_date_29th_feb(self):
        # Check formatting on a valid leap day
        self.assertEqual(get_formatted_date("2016-02-29 01:01:01"), "29 Feb 2016 01:01")
        # Should not format a leap day on a non leap year
        self.assertEqual(get_formatted_date("2018-02-29 01:01:01"), "2018-02-29 01:01:01")

    def test_get_formatted_date_returns_malformed_dates(self):
        # Strings not in the correct format or invalid dates should be returned as given and a exception logged
        self.assertEqual(get_formatted_date(""), "")
        self.assertEqual(get_formatted_date("1999-12-32 23:59:59"), "1999-12-32 23:59:59")

    def test_convert_to_bst_from_utc_during_bst(self):
        # 13th Jun 2018 at 14.12 should return 13th Jun 2018 at 15.12
        datetime_parsed = datetime(2018, 6, 13, 14, 12, 0, tzinfo=timezone.utc)
        returned_datetime = localise_datetime(datetime_parsed)
        # Check date returned is in BST format
        self.assertEqual(datetime.strftime(returned_datetime, "%Y-%m-%d %H:%M:%S"), "2018-06-13 15:12:00")

    def test_convert_to_bst_from_utc_during_gmt(self):
        # 13th Feb 2018 at 14.12 should return 13th Feb 2018 at 14.12
        datetime_parsed = datetime(2018, 2, 13, 14, 12, 0, tzinfo=timezone.utc)
        returned_datetime = localise_datetime(datetime_parsed)
        # Check date returned is in BST format
        self.assertEqual(datetime.strftime(returned_datetime, "%Y-%m-%d %H:%M:%S"), "2018-02-13 14:12:00")

    def test_format_datetime_to_string(self):
        tests = [
            ["2020-06-22T06:00:00.000Z", "Monday 22 Jun 2020"],
            ["2020-01-01T15:30:00.000Z", "Wednesday 01 Jan 2020"],
            ["2020-06-22T06:00:00.000Z", "%A %d %b %Y %H:%M", "Monday 22 Jun 2020 06:00"],
            ["2020-03-16T15:59:00.000Z", "%A %d %b %Y %H:%M", "Monday 16 Mar 2020 15:59"],
            ["bad date", "N/A"],
            [None, "N/A"],
        ]
        for test in tests:
            if len(test) == 3:
                output = format_datetime_to_string(test[0], test[1], False)
                expected_output = test[2]
            else:
                output = format_datetime_to_string(test[0], localise=True)
                expected_output = test[1]

            self.assertEqual(output, expected_output)

    def test_format_datetime_to_string_localised_bst(self):
        datetime = "2020-06-22T06:00:00.000Z"
        dateformat = "%A %d %b %Y %H:%M"
        expected = "Monday 22 Jun 2020 07:00"
        output = format_datetime_to_string(datetime, dateformat, True)
        self.assertEqual(output, expected)

    def test_format_datetime_to_string_localised_gmt(self):
        datetime = "2020-01-22T06:00:00.000Z"
        dateformat = "%A %d %b %Y %H:%M"
        expected = "Wednesday 22 Jan 2020 06:00"
        output = format_datetime_to_string(datetime, dateformat, True)
        self.assertEqual(output, expected)
