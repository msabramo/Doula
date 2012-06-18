import os
import unittest
from mock import patch
from mock import call
from doula.models.sites import Application
from doula.models.sites import Package


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_compare_url(self):
        app = Application('test_app', 'site_name', 'test_node', 'http://test.com')
        app.remote = 'git@code.corp.surveymonkey.com:DevOps/WebApp1.git'
        app.last_tag_app = '1.0.3'
        app.current_branch_app = 'master'

        tags = [{'name': '1.0.3', 'message': 'last tag message', 'date': '8484848'}]
        app.add_tags_from_dict(tags)

        compare_url = 'http://code.corp.surveymonkey.com'
        compare_url += '/DevOps/test_app/compare/1.0.3...master'

        self.assertEqual(app.get_compare_url(), compare_url)

    def test_freeze_requirements(self):
        app = Application('test_app', 'site_name', 'test_node', 'http://test.com')
        packages = []

        packages.append(Package('mnn', '1'))
        packages.append(Package('ebd', '2'))
        packages.append(Package('dbc', '2'))
        packages.append(Package('abc', '1'))
        app.packages = packages

        expected = "abc==1\n"
        expected += "dbc==2\n"
        expected += "ebd==2\n"
        expected += "mnn==1\n"

        self.assertEqual(app.freeze_requirements(), expected)


class PackageTests(unittest.TestCase):
    def setUp(self):
        pass

    def testDown(self):
        pass

    def make_one(self):
        return Package("dummycode", "1.3.1")

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

if __name__ == '__main__':
    unittest.main()
