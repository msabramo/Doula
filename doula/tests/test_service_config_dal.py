import unittest
from doula.models.service_config_dal import ServiceConfigDAL
from doula.config import Config


class ServiceConfigDALTests(unittest.TestCase):
    def setUp(self):
        #Redis.env = 'dev'

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

        self.assertTrue(sc_dal._get_last_service_config('billweb'))


if __name__ == '__main__':
    unittest.main()
