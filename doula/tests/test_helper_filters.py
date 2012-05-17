import json
import unittest

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
    

if __name__ == '__main__':
    unittest.main()