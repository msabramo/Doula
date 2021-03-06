import unittest
from datetime import datetime
import calendar

from doula.helper_filters import *


class HelperTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_natural_sort(self):
        l = ['elm1', 'elm7', 'elm4', 'elm0']
        nat_l = natural_sort(l)

        self.assertEqual(nat_l[0], 'elm0')
        self.assertEqual(nat_l[1], 'elm1')
        self.assertEqual(nat_l[2], 'elm4')
        self.assertEqual(nat_l[3], 'elm7')

    def test_version_number_to_git_tag(self):
        name = '1.2.7b11-admintools-new'
        expected = '1.2.7b11-admintools_new'
        result = version_number_to_git_tag(name)

        self.assertEqual(result, expected)

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
        day = now.day - 1
        month = now.month

        if day == 0:
            if str(month) == '1':
                month = 12
            else:
                month = month - 1

            day = calendar.monthrange(now.year, month)[1]

        yesterday = datetime(now.year, month, day, 10, 31, 10)
        yester_val = yesterday.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(yester_val)

        self.assertEqual('Yesterday at 10:31 AM', result)

        # expect 5 days ago at 10:31 AM
        if now.day > 5:
            days_ago = datetime(now.year, now.month, now.day - 5, 10, 31, 10)
        else:
            # backup to previous month
            month = now.month - 1
            if str(month) == '0':
                month = 12

            last_day_prev_month = calendar.monthrange(now.year, month - 1)[1]
            remaining_negative_days = now.day - 5
            new_day = last_day_prev_month + remaining_negative_days
            days_ago = datetime(now.year, month, new_day, 10, 31, 10)

        days_ago_val = days_ago.strftime("%Y-%m-%dT%X+02:00")
        result = relative_datetime(days_ago_val)

        self.assertEqual('5 days ago at 10:31 AM', result)

        # expect 2 months ago
        month = now.month - 2
        year  = now.year

        if month < 1:
            month = 12 + month
            year = year - 1

        days_ago = datetime(year, month, now.day - 2, 10, 31, 10)
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

    def test_formatted_github_day(self):
        date = "2012-02-15 10:12:01"
        result = formatted_github_day(date)

        self.assertEqual("February 15, 2012", result)

        date = "2012-10-02 10:12:01 +02:00"
        result = formatted_github_day(date)

        self.assertEqual("October 02, 2012", result)

        date = '2012-05-08 14:15:31 -0700'
        result = formatted_github_day(date)
        self.assertEqual("May 08, 2012", result)

    def test_formatted_github_day_and_time(self):
        date = "2012-02-15 10:12:01"
        result = formatted_github_day_and_time(date)

        self.assertEqual("February 15, 2012 10:12 AM", result)

        date = "2012-10-02 10:12:01 +02:00"
        result = formatted_github_day_and_time(date)

        self.assertEqual("October 02, 2012 10:12 AM", result)

        date = '2012-05-08 14:15:31 -0700'
        result = formatted_github_day_and_time(date)
        self.assertEqual("May 08, 2012 02:15 PM", result)


if __name__ == '__main__':
    unittest.main()
