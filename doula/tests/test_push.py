import os
import unittest
import commands
from mock import Mock
from doula.models.push import Push

class PushTests2(unittest.TestCase):

    def test_stuff(self):
        push = Push('createweb', 'localhost', 
                    'tsabat', '/opt/webapp',
                    'http://yorick:9003',
                    '~/.ssh/id_rsa',
                    '',
                    True)

        _, u = commands.getstatusoutput('whoami')
        push.fabric_user = Mock(return_value=u)
        push._chown = Mock()
        push.install_assets = Mock(return_value=(True, True))
        push.packages(['requests'])

if __name__ == '__main__':
    unittest.main()


#class PushTests():

    #def get_config(self):
        #key = os.path.expanduser('~/.ssh/id_rsa')
        #return {
            #'bambino.webapp_dir': '/opt/webapp',
            #'doula.cheeseprism_url': 'http://yorick:9003',
            #'doula.assets.dir': '/opt/smassets',
            #'doula.keyfile_path': key
        #}

    #def test_push(self):
        #config = self.get_config()
        #job_dict = {
            #'id': 111,
            #'user_id': 'tbone',
            #'service': 'createweb',
            #'site': 'localhost',
            #'packages': ['requests']
        #}


        #_, user = commands.getstatusoutput('whoami')
        #jobs.fabric_user = Mock(side_effect=lambda *args, **kwargs: user)

        #successes, failures = jobs.release_service(config, job_dict, True)
        #print successes, failures


