import os
import unittest

from mock import patch
from mock import call

from doula.models.package import Package


class PackageTests(unittest.TestCase):
    def setUp(self):
        pass

    def testDown(self):
        pass

    def make_one(self):
        return Package("dummycode", "0.1.3", "git@code.corp.surveymonkey.com:joed")

    def test_repo(self):
        package = self.make_one()
        with package.repo() as repo:
            self.assertEqual(os.path.exists('repos'), True)
            self.assertEqual(hasattr(repo, 'working_dir'), True)
        self.assertEqual(os.path.exists(repo.working_dir), False)

    def test_update_version(self):
        package = self.make_one()
        with package.repo() as repo:
            package.update_version(repo, "1.3.2")

            setup_py_path = os.path.join(repo.working_dir, 'setup.py')
            with open(setup_py_path, 'r+') as f:
                for line in f.readlines():
                    if line.startswith('version'):
                        self.assertEqual(line, "version = '1.3.2'\n")

    @patch('git.Repo')
    def test_commit(self, Repo):
        package = self.make_one()
        package.commit(Repo, ['setup.py'], 'DOULA: Updating Version.')

        self.assertEqual(Repo.index.add.called, True)
        self.assertEqual(Repo.index.commit.called, True)
        self.assertEqual(Repo.index.add.call_args_list, [call(['setup.py'])])
        self.assertEqual(Repo.index.commit.call_args_list, [call('DOULA: Updating Version.')])

    @patch('git.Repo')
    def test_push(self, Repo):
        package = self.make_one()
        package.push(Repo, "origin")

        origin = Repo.remotes["origin"]
        self.assertEqual(origin.pull.called, True)
        self.assertEqual(origin.push.called, True)
