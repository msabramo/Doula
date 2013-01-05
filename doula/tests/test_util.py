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

    def test_find_package_and_version_in_pip_freeze_text(self):
        text = 'sqlalchemy-migrate==0.6.1'
        result = find_package_and_version_in_pip_freeze_text(text)

        self.assertEqual(result['sqlalchemy-migrate'], '0.6.1')

        text = 'beaker-extensions==0.1.2dev'
        result = find_package_and_version_in_pip_freeze_text(text)
        self.assertEqual(result['beaker-extensions'], '0.1.2dev')

        text = 'Not bad. sqlalchemy-migrate==0.6.1'
        result = find_package_and_version_in_pip_freeze_text(text)

        self.assertEqual(len(result.keys()), 0)

        text = '-e git+git@code.corp.surveymonkey.com:panel/panel.git@6236d7b#egg=panel-1.0.28-py2.6-dev'
        result = find_package_and_version_in_pip_freeze_text(text)

        self.assertEqual(len(result.keys()), 0)


if __name__ == '__main__':
    unittest.main()
