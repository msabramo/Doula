from doula.config import Config
from doula.models.service_config import ServiceConfig
from doula.models.service_config_dal import ServiceConfigDAL
import unittest


class ServiceConfigDALTests(unittest.TestCase):
    # This unit test has to be run with real redis since it depends on
    # features not implemented on mock redis
    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.config.org': 'config',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
        }

        Config.load_config(settings)

    def testDown(self):
        pass

    def test_update_service_config_data(self):
        sc_dal = ServiceConfigDAL()
        sc_dal.update_service_config_data()

        self.assertTrue(sc_dal._get_latest_service_config('mt1', 'billweb'))
        self.assertTrue(sc_dal._get_latest_service_config('mt2', 'billweb'))
        self.assertTrue(sc_dal._get_latest_service_config('mt3', 'billweb'))

    def test_get_service_configs(self):
        sc_dal = ServiceConfigDAL()
        service_configs = sc_dal.get_service_configs('mt1', 'billweb')

        self.assertEqual(len(service_configs), 10)


if __name__ == '__main__':
    unittest.main()
