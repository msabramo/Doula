from doula.util import *
import unittest


class UtilTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_next_version(self):
        result = next_version('0.1.3')
        self.assertEqual(result, '0.1.4')

        result = next_version('0.1.9')
        self.assertEqual(result, '0.1.91')

        result = next_version('2.9.9')
        self.assertEqual(result, '2.9.91')

        result = next_version('9.9rc')
        self.assertEqual(result, '9.91rc')


if __name__ == '__main__':
    unittest.main()
