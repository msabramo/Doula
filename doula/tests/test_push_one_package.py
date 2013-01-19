from doula.config import Config
from doula.models.package import Package
import os
import uuid
import unittest

class PackageTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.config.org': 'config',
            'doula.cheeseprism_url': 'http://yorick.corp.surveymonkey.com:9003',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69',
            'doula.session.secret': 'd4c84eed159abf6049dc53c1aa7ec85edb150fb2'
        }

        Config.load_config(settings)

    def test_build_package(self):
        job_dict = {
            'version': '0.17.6-PAYMENTGATEWAY_DIGITAL_RIVER',
            'user_id': 'alexv',
            'package_name': 'paymentgateway',
            'service': 'paymentgateway',
            'branch': 'PAYMENTGATEWAY_DIGITAL_RIVER',
            'remote': 'git@code.corp.surveymonkey.com:devmonkeys/paymentgateway.git',
            'job_type': 'build_new_package',
            'site': 'mt3',
            'id': uuid.uuid1()
        }

        p = Package(job_dict['package_name'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

if __name__ == '__main__':
    unittest.main()
