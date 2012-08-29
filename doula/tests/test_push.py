import os
import unittest
import os
import json

from mock import patch
from mock import call

from doula.models.push import Push
from doula import jobs as jobs

class PushTests(unittest.TestCase):

    def get_config(self):
        key = os.path.expanduser('~/.ssh/id_rsa_doula')
        return {
            'bambino.web_app_dir': '/opt/webapp',
            'doula.cheeseprism_url': 'http://mtclone:6543/index',
            'doula.keyfile_path': key
        }

    def test_push(self):

        #push = Push(
                #job_dict['service_name'],
                #job_dict['username'],
                #job_dict['email'],
                #Config.get('bambino.web_app_dir'),
                #Config.get('doula.cheeseprism_url'),
                #Config.get('doula.keyfile_path'),
                #job_dict['site_name_or_node_ip']


        config = self.get_config()
        job_dict = {
            'id': 111,
            'service_name': 'anonweb',
            'username': 'tbone',
            'email': 'tims@surveymonkey.com',
            'site_name_or_node_ip': 'mt-99',
            'packages': ['requests']
        }
        successes, failures = jobs.push_service_environment(config, job_dict, True)
        print successes, failures
