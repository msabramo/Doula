from doula.config import Config
from doula.models.package_java import PackageJava
from mock import call
from mock import patch
import os
import uuid
import unittest


class PackageJavaTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.cheeseprism_url': 'http://yorick:9003',
            'doula.cheeseprism_package_index_path': '/var/www/python-pkgindex',
            'doula.keyfile_path': '~/.ssh/id_rsa_doula'
        }
        Config.load_config(settings)

    def testDown(self):
        pass

    def test_distribute(self):
        job_dict = {
            'version': str(uuid.uuid1()),
            'user_id': 'alexv',
            'package_name': 'userdal',
            'service': 'userdal',
            'branch': 'master',
            'remote': 'git@code.corp.surveymonkey.com:tbone/userdal.git',
            'job_type': 'build_new_package',
            'site': 'alexs-macbook-pro-4.local',
            'id': 'bc255ebaf6da11e1b07fb8f6b1191577'
        }

        p = PackageJava(job_dict['package_name'], '9.9.9', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

if __name__ == '__main__':
    unittest.main()
