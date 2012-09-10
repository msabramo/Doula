from doula.config import Config
from doula.models.package import Package
from mock import call
from mock import patch
import os
import uuid
import unittest


class PackageTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.cheeseprism_url': 'http://mt-99:6789'
        }
        Config.load_config(settings)

    def testDown(self):
        pass

    def make_one(self):
        return Package("dummycode", "0.1.3", "git@code.corp.surveymonkey.com:joed")

    def test_distribute(self):
        job_dict = {
            'version': uuid.uuid1(),
            'user_id': 'alexv',
            'package_name': 'billweb',
            'service': 'billweb',
            'branch': 'stwopay',
            'remote': 'git@code.corp.surveymonkey.com:devmonkeys/BillWeb.git',
            'job_type': 'push_to_cheeseprism',
            'site': 'alexs-macbook-pro-4.local',
            'id': 'bc255ebaf6da11e1b07fb8f6b1191577'
        }

        p = Package(job_dict['package_name'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

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
        package.commit(Repo, ['setup.py'], 'bump version')

        self.assertEqual(Repo.index.add.called, True)
        self.assertEqual(Repo.index.commit.called, True)
        self.assertEqual(Repo.index.add.call_args_list, [call(['setup.py'])])
        self.assertEqual(Repo.index.commit.call_args_list, [call('bump version')])

    @patch('git.Repo')
    def test_push(self, Repo):
        package = self.make_one()
        package.push(Repo, "origin")

        origin = Repo.remotes["origin"]
        self.assertEqual(origin.pull.called, True)
        self.assertEqual(origin.push.called, True)

    def test_get_updated_setup_dot_py(self):
        package = self.make_one()
        lines = []
        lines.append('** Copyright SurveyMonkey Wed, 7 Jul 2011 15:13:22 **')
        lines.append('Source:      devmonkeys/UserWeb *master 3fffaf9')
        lines.append('Released by: ringo')
        lines.append('version = "0.9.9"')

        text = package.get_updated_setup_dot_py(
            lines, '0.1.1', 'test', 'git@github.com:Doula/Doula.git',
            '224c0e7a4c967c1266c20a2290e')

        self.assertTrue("Doula/Doula *test 224c0e7" in text)
        self.assertTrue("Released by:" in text)
        self.assertTrue("version = '0.1.1'" in text)

if __name__ == '__main__':
    unittest.main()
