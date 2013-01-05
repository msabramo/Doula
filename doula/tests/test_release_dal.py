from doula.cache import Redis
from doula.config import Config
from doula.models.release_dal import ReleaseDAL
import unittest


class ReleaseDALTests(unittest.TestCase):
    def setUp(self):
        Redis.env = 'dev'
        self.releaseDAL = ReleaseDAL()

        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
        }

        Config.load_config(settings)

    def testDown(self):
        pass

    def test_next_release(self):
        next = self.releaseDAL.next_release('site_name', 'service_name')

        self.assertEqual(next, 1)

        next = self.releaseDAL.next_release('site_name', 'service_name')
        self.assertEqual(next, 2)

        next = self.releaseDAL.next_release('site_name', 'service_name')
        self.assertEqual(next, 3)

        next = self.releaseDAL.next_release('site_name1', 'service_name1')
        self.assertEqual(next, 1)

if __name__ == '__main__':
    unittest.main()
