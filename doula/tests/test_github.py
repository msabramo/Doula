from doula.config import Config
from doula.github.github import *
import unittest


class GithubTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github.packages.org': 'doulaweb',
            'doula.github.appenvs.org': 'AppEnv'
        }
        Config.load_config(settings)
        pass

    def tearDown(self):
        pass

    def test_pull_devmonkeys_repos(self):
        repos = pull_devmonkeys_repos()

        for repo in repos:
            # Ensure the name is true
            self.assertTrue(repo['name'])

    def test_pull_appenv_repos(self):
        repos = pull_appenv_repos('mt1')

        for name, repo in repos.iteritems():
            # Ensure the name is true
            self.assertTrue(name)

    def test_is_doula_appenv_commit(self):
        commit = """
        Pushed AnWeb==2.0.95
        ##################
        pip freeze:
        ##################
        """
        result = is_doula_appenv_commit(commit)
        self.assertTrue(result)

        result = is_doula_appenv_commit("bad commit")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
