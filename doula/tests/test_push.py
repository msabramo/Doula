import unittest
import commands
from mock import Mock
from doula.models.push import Push
from doula.config import Config

class PushTests2(unittest.TestCase):

    def setUp(self):
        settings = {
            'doula.github.token': '3cf79e0b2e1abe84a519227640fd6251164df61b'
        }

        Config.load_config(settings)

    def test_stuff(self):
        push = Push(
            service_name='createweb',
            node_ip='localhost',
            username='tsabat',
            web_app_dir='/opt/webapp',
            cheeseprism_url='http://yorick:9003',
            keyfile='~/.ssh/id_rsa',
            outdir='',
            site='mt1',
            debug=True)

        _, u = commands.getstatusoutput('whoami')
        push.fabric_user = Mock(return_value=u)
        push._chown = Mock()
        push.install_assets = Mock(return_value=(True, True))
        push.packages_to_node({'packages': {'requests': '0.13.0'}, 'is_rollback': True, 'etc_sha1': '93f481d56d3e3e7c939bc172507106d76ed546f1'})

if __name__ == '__main__':
    unittest.main()
