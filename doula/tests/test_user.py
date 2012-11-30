from doula.cache import Redis
from doula.config import Config
from doula.models.user import User
import unittest


class UserTests(unittest.TestCase):

    def setUp(self):
        Redis.env = 'dev'
        self.redis = Redis.get_instance()
        self.redis.flushdb()

        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69',
            'doula.cheeseprism_url': 'http://yorick.corp.surveymonkey.com:9003'
        }

        Config.load_config(settings)

    def test_save(self):
        user = {
            "username": 'alexv'
        }

        User.save(user)
        users = User.users()

        self.assertEqual(users.pop()['username'], 'alexv')

    def test_find(self):
        user = {
            "username": 'alexv'
        }

        User.save(user)
        self.assertNotEqual(User.find('alexv'), None)


if __name__ == '__main__':
    unittest.main()
