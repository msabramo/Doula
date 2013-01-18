import unittest
from doula.jobs import add_webhook_callbacks
from doula.config import Config

class JobTests(unittest.TestCase):

    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.config.org': 'config',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69',
            'doula.github.webhook.url' : 'http://doula.corp.surveymonkey.com/webhook/callbacks'
        }

        Config.load_config(settings)

    def test_set_webhooks(self):
        add_webhook_callbacks()
        pass


if __name__ == '__main__':
    unittest.main()
