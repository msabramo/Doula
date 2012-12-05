from doula.config import Config
from doula.github import *
import unittest


class GithubTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
        }

        Config.load_config(settings)

    def tearDown(self):
        pass

    def test_pull_doula_admins(self):
        admins = pull_doula_admins()
        self.assertTrue(len(admins))

    def test_pull_devmonkeys_repos(self):
        repos = pull_devmonkeys_repos()

        for name, repo in repos.iteritems():
            # Ensure the name is true
            self.assertTrue(repo['name'])

    def test_pull_appenv_repos(self):
        repos = pull_appenv_repos()

        for name, repo in repos.iteritems():
            # Ensure the name is true
            self.assertTrue(name)


if __name__ == '__main__':
    unittest.main()
