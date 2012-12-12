import os
import unittest
from doula.models.push_java import PushJava
from doula.config import Config

class PushTestsJava(unittest.TestCase):

    def setUp(self):
        settings = {
            'doula.cheeseprism_url': 'http://yorick:9003',
            'doula.cheeseprism_package_index_path': '/var/www/python-pkgindex',
            'doula.keyfile_path': '~/.ssh/id_rsa_doula'
        }
        Config.load_config(settings)

    def test_push(self):

        job_dict = {
            'id': 111,
            'user_id': 'tbone',
            'service_name': 'createweb',
            'site_name_or_node_ip': 'mt-99',
            'packages': ['requests']
        }

        service = PushJava(
                'userdal', 
                '33.33.33.10', 
                'vagrant', 
                '/opt/java', 
                'http://yorick:9003',
                '~/.ssh/id_rsa_doula',  
                '',
                True)

        service.release_service(['UserAccount.war==9.9.9'])

if __name__ == '__main__':
    unittest.main()
