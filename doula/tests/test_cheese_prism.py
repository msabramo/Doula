from doula.cache import Redis
from doula.cheese_prism import CheesePrism
from doula.cheese_prism import PythonPackage
from doula.config import Config
from doula.util import comparable_name
import json
import unittest


class CheesePrismTests(unittest.TestCase):
    def setUp(self):
        Redis.env = 'dev'
        self.redis = Redis.get_instance()
        self.redis.flushdb()

        settings = {
            'doula.cheeseprism_url': 'http://yorick.corp.surveymonkey.com:9003'
        }
        Config.load_config(settings)

    def tearDown(self):
        pass

    def test_pull_all_packages(self):
        all_packages = CheesePrism.pull_all_packages()

        self.assertTrue(len(all_packages))

    def test_get_last_version(self):
        # Test the simple PythonPackage class
        versions = ['0.3.4', '1.0.2', '1.5', '1.0.4', '1.4.5']
        pp = PythonPackage('test_package', versions)

        self.assertEqual(pp.get_last_version(), '1.5')

    def test_find_package_by_name(self):
        package_by_name = {
            "comparable_name": "testpackage",
            "name": "test_package",
            "versions": ["0.6.7"]
        }

        name = comparable_name("test_package")

        self.redis.set('cheeseprism:package:' + name, json.dumps(package_by_name))
        python_package = CheesePrism.find_package_by_name('test_package')

        self.assertEqual(python_package.name, 'test_package')
        self.assertEqual(python_package.get_last_version(), "0.6.7")


if __name__ == '__main__':
    unittest.main()
