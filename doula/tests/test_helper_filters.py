import unittest
from datetime import datetime
import calendar

from doula.helper_filters import *


class HelperTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_isodate(self):
        date_string = "2012-05-05T16:30:20.140762"
        pretty_date = format_isodate(date_string)
        self.assertEqual('May 05, 2012 04:30 PM', pretty_date)

    def test_relative_datetime(self):
        now = datetime.now()

        # Test for Today at 12:01 AM
        today = datetime(now.year, now.month, now.day, 00, 1, 10)
        today_val = today.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(today_val)

        self.assertEqual("Today at 12:01 AM", result)

        # expect Yesterday at 10:31 AM
        yesterday = datetime(now.year, now.month, now.day - 1, 10, 31, 10)
        yester_val = yesterday.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(yester_val)

        self.assertEqual('Yesterday at 10:31 AM', result)

        # expect 5 days ago at 10:31 AM
        if now.day > 5:
            days_ago = datetime(now.year, now.month, now.day - 5, 10, 31, 10)
        else:
            # backup to previous month
            last_day_prev_month = calendar.monthrange(now.year, now.month - 1)[1]
            remaining_negative_days = now.day - 5
            new_day = last_day_prev_month + remaining_negative_days
            days_ago = datetime(now.year, now.month - 1, new_day, 10, 31, 10)

        days_ago_val = days_ago.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(days_ago_val)

        self.assertEqual('5 days ago at 10:31 AM', result)

        # expect 2 months ago
        days_ago = datetime(now.year, now.month - 2, now.day - 2, 10, 31, 10)
        days_ago_val = days_ago.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(days_ago_val)

        self.assertEqual('2 months ago', result)

        days_ago = datetime(now.year - 2, now.month, now.day, 10, 31, 10)
        days_ago_val = days_ago.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(days_ago_val)

        self.assertEqual('2 years ago', result)

    def test_formatted_day(self):
        date = "2012-02-15T10:12:01+02:00"
        result = formatted_day(date)

        self.assertEqual("February 15, 2012", result)

        date = "2012-10-02T10:12:01+02:00"
        result = formatted_day(date)

        self.assertEqual("October 02, 2012", result)


if __name__ == '__main__':
    unittest.main()
