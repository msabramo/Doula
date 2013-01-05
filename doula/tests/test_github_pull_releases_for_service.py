from doula.config import Config
from doula.github import *
import unittest


class GithubTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'FakeAppEnvs',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
        }

        Config.load_config(settings)

    def test_pull_releases_for_service(self):
        releases = pull_releases_for_service('createweb')

        for branch, release in releases.iteritems():
            self.assertTrue(len(release) > 0)

    def test_pull_appenv_service_names(self):
        names = pull_appenv_service_names()
        self.assertTrue(len(names) > 0)


if __name__ == '__main__':
    unittest.main()
