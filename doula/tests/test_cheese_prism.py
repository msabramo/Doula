from doula.config import Config
from doula.github import *
from doula.cheese_prism import CheesePrism
import unittest


class CheesePrismTests(unittest.TestCase):
    def setUp(self):
        Redis.env = 'dev'
        Redis.get_instance().flushdb()
        settings = {
            'doula.cheeseprism_url': 'http://yorick.corp.surveymonkey.com:9003'
        }
        Config.load_config(settings)

    def tearDown(self):
        pass

    def test_pull_all_packages(self):
        all_packages = CheesePrism.pull_all_packages()

        self.assertTrue(len(all_packages))


if __name__ == '__main__':
    unittest.main()
