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
            'service': 'createweb',
            'site': 'mtclone',
            'packages': ['requests']
        }

        successes, failures = jobs.release_service(config, job_dict, True)
        print successes, failures
