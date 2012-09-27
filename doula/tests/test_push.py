import os
import unittest
from doula import jobs as jobs


class PushTests(unittest.TestCase):

    def get_config(self):
        key = os.path.expanduser('~/.ssh/id_rsa_doula')
        return {
            'bambino.webapp_dir': '/opt/webapp',
            'doula.cheeseprism_url': 'http://mtclone:6543',
            'doula.assets.dir': '/opt/smassets',
            'doula.keyfile_path': key
        }

    def test_push(self):

        config = self.get_config()
        job_dict = {
            'id': 111,
            'user_id': 'tbone',
            'service_name': 'createweb',
            'site_name_or_node_ip': 'mt-99',
            'packages': ['requests']
        }

        successes, failures = jobs.push_service_environment(config, job_dict, True)
        print successes, failures
