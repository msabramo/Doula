from doula.config import Config
from doula.github.github import *
import unittest


class GithubTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github_org': 'doulaweb'
        }
        Config.load_config(settings)
        pass

    def tearDown(self):
        pass

    def test_pull_devmonkeys_repos(self):
        # alextodo, add testing to the repos
        repos = pull_devmonkeys_repos()


if __name__ == '__main__':
    unittest.main()
