import os
import unittest
import commands
from mock import Mock
from doula.models.push import Push
from mock import patch
from mockredis import MockRedis
from doula.config import Config
import ipdb

class PushTests2(unittest.TestCase):

    def setUp(self):
        settings = {
            'doula.github.token': '3cf79e0b2e1abe84a519227640fd6251164df61b'
        }

        Config.load_config(settings)

    def test_stuff(self):
        push = Push('createweb', 'localhost',
                    'tsabat', '/opt/webapp',
                    'http://yorick:9003',
                    '~/.ssh/id_rsa',
                    '',
                    'mt1',
                    True)

        _, u = commands.getstatusoutput('whoami')
        push.fabric_user = Mock(return_value=u)
        push._chown = Mock()
        push.install_assets = Mock(return_value=(True, True))
        push.packages({'packages': {'requests': '0.13.0'}, 'is_rollback': True, 'etc_sha1': '93f481d56d3e3e7c939bc172507106d76ed546f1'})

if __name__ == '__main__':
    unittest.main()
