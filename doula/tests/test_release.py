from doula.models.package import Package
from doula.models.release import Release
from doula.models.service import Service
from doula.config import Config
import unittest
import pdb
import json
import os


class ReleaseTests(unittest.TestCase):

    def setUp(self):
        settings = {
            'redis.host': 'localhost',
            'redis.port': 6379,
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
        }

        Config.load_config(settings)

        self.repo = {
            'commits': [
                {
                    'author': 'quezo',
                    'date': '2012-11-10T00:20:03+00:00',
                    'message': """Pushedpanel==1.0.24
                        ##################
                        pipfreeze:
                        ##################
                        Beaker==1.5.4
                        Chameleon==1.3.0-rc1
                        Elixir==0.7.1
                        """
                }
            ],
            'name': 'panel'
        }

    def testDown(self):
        pass

    def test_build_release_from_repo(self):
        release = Release.build_release_from_repo(
                                                self.repo,
                                                self.repo['commits'][0])

        self.assertEqual(release.author, 'quezo')
        self.assertEqual(len(release.packages), 3)

    def test__build_release_packages_dict(self):
        """Build a dict from the release packages list"""

        packages = []
        packages.append(Package('Anweb', '1.1'))
        packages.append(Package('create', '1.3'))

        release = Release('author', "2012-11-10T00:20:03+00:00", "commit_message", "branch", packages)

        result = release._build_release_packages_dict()
        self.assertEqual(result['anweb'].version, '1.1')
        self.assertEqual(result['create'].version, '1.3')

    def test__find_packages_to_add(self):
        packages = []
        packages.append(Package('Anweb', '1.1'))
        packages.append(Package('create', '1.3'))

        release = Release('author', "2012-11-10T00:20:03+00:00", "commit_message", "branch", packages)
        release_packages = release._build_release_packages_dict()

        service_data = {
            "current_branch_app": "mt3",
            "name": "anweb",
            "tags": [],
            "packages": {
                "Anweb": {
                    "version": "0.3",
                    "name": "Anweb"
                },
                "smlib": {
                    "version": "1.2.7",
                    "name": "smlib"
                }
            },
            "config": {
                "latest_sha": "b2394728900d20d98bf6fff21f89387c52e0282c",
                "author": "kael",
                "changed_files": {},
                "is_up_to_date": 'false',
                "sha": "7741d17cb6b48a699e1404f86cedede6efe7891a",
                "branch": "mt3",
                "formatted_date": "October 05, 2012 01:24 PM",
                "date": "2012-10-05 13:24:31 -0700",
                "message": "Adjusted log time format to indicate local time.",
                "repo_name": "anweb"
            }
        }

        service = Service(**service_data)
        packages_to_add = release._find_packages_to_add(service, release_packages)

        self.assertTrue('create' in packages_to_add)
        self.assertEqual(packages_to_add['create'].version, '1.3')

    def test__find_packages_that_will_be_subtracted(self):
        packages = []
        packages.append(Package('Anweb', '1.1'))
        packages.append(Package('create', '1.3'))

        release = Release('author', "2012-11-10T00:20:03+00:00", "commit_message", "branch", packages)
        release_packages = release._build_release_packages_dict()

        service_data = {
            "current_branch_app": "mt3",
            "name": "anweb",
            "tags": [],
            "packages": {
                "Anweb": {
                    "version": "0.3",
                    "name": "Anweb"
                },
                "smlib": {
                    "version": "1.2.7",
                    "name": "smlib"
                }
            },
            "config": {
                "latest_sha": "b2394728900d20d98bf6fff21f89387c52e0282c",
                "author": "kael",
                "changed_files": {},
                "is_up_to_date": 'false',
                "sha": "7741d17cb6b48a699e1404f86cedede6efe7891a",
                "branch": "mt3",
                "formatted_date": "October 05, 2012 01:24 PM",
                "date": "2012-10-05 13:24:31 -0700",
                "message": "Adjusted log time format to indicate local time.",
                "repo_name": "anweb"
            }
        }

        service = Service(**service_data)
        packages_to_subtract = release._find_packages_that_will_be_subtracted(service, release_packages)

        self.assertTrue('smlib' in packages_to_subtract)
        self.assertEqual(packages_to_subtract['smlib'].version, '1.2.7')

    def test__find_same_packages_with_diff_versions(self):
        packages = []
        packages.append(Package('Anweb', '1.1'))
        packages.append(Package('create', '1.3'))

        release = Release('author', "2012-11-10T00:20:03+00:00", "commit_message", "branch", packages)
        release_packages = release._build_release_packages_dict()

        service_data = {
            "current_branch_app": "mt3",
            "name": "anweb",
            "tags": [],
            "packages": {
                "Anweb": {
                    "version": "0.3",
                    "name": "Anweb"
                },
                "smlib": {
                    "version": "1.2.7",
                    "name": "smlib"
                }
            },
            "config": {
                "latest_sha": "b2394728900d20d98bf6fff21f89387c52e0282c",
                "author": "kael",
                "changed_files": {},
                "is_up_to_date": 'false',
                "sha": "7741d17cb6b48a699e1404f86cedede6efe7891a",
                "branch": "mt3",
                "formatted_date": "October 05, 2012 01:24 PM",
                "date": "2012-10-05 13:24:31 -0700",
                "message": "Adjusted log time format to indicate local time.",
                "repo_name": "anweb"
            }
        }

        service = Service(**service_data)
        changed_packages = release._find_same_packages_with_diff_versions(service, release_packages)

        self.assertTrue('anweb' in changed_packages)

        self.assertEqual(changed_packages['anweb']['package'].comparable_name, 'anweb')
        self.assertEqual(changed_packages['anweb']['release_version'], '1.1')
        self.assertEqual(changed_packages['anweb']['service_version'], '0.3')

    def test_diff_service_and_release(self):
        packages = []
        packages.append(Package('Anweb', '1.1'))
        packages.append(Package('create', '1.3'))

        release = Release('author', "2012-11-10T00:20:03+00:00", "commit_message", "branch", packages)
        release_packages = release._build_release_packages_dict()

        service_data = {
            "current_branch_app": "mt3",
            "name": "anweb",
            "site_name": "mt3",
            "tags": [],
            "packages": {
                "Anweb": {
                    "version": "0.3",
                    "name": "Anweb"
                },
                "smlib": {
                    "version": "1.2.7",
                    "name": "smlib"
                }
            },
            "config": {
                "latest_sha": "b2394728900d20d98bf6fff21f89387c52e0282c",
                "author": "kael",
                "changed_files": {},
                "is_up_to_date": 'false',
                "sha": "7741d17cb6b48a699e1404f86cedede6efe7891a",
                "branch": "mt3",
                "formatted_date": "October 05, 2012 01:24 PM",
                "date": "2012-10-05 13:24:31 -0700",
                "message": "Adjusted log time format to indicate local time.",
                "repo_name": "anweb"
            }
        }

        service = Service(**service_data)
        release_packages = release.diff_service_and_release(service)

        self.assertTrue(release_packages['changed_packages']['anweb']['package'])
        self.assertTrue(release_packages['changed_packages'])
        self.assertTrue(release_packages['packages_to_add'])
        self.assertTrue(release_packages['packages_to_subtract'])

    def test_diff_service_and_release_from_files(self):
        packages = []

        current_dir = os.path.dirname(__file__)

        releases_file = open(current_dir + '/test_release_release_packages.json')
        releases_dict = json.loads(releases_file.read())
        releases_file.close()

        for comparable_name, pckg in releases_dict.iteritems():
            packages.append(Package(pckg["name"], pckg["version"]))

        release = Release('author', "2012-11-10T00:20:03+00:00", "commit_message", "branch", packages)
        release_packages = release._build_release_packages_dict()

        service_packages_file = open(current_dir + "/test_release_service_packages.json")
        services_packages_dict = json.loads(service_packages_file.read())
        service_packages_file.close()

        service_data = {
            "current_branch_app": "mt3",
            "name": "anweb",
            "site_name": "mt3",
            "tags": [],
            "packages": services_packages_dict,
            "config": {
                "latest_sha": "b2394728900d20d98bf6fff21f89387c52e0282c",
                "author": "kael",
                "changed_files": {},
                "is_up_to_date": 'false',
                "sha": "7741d17cb6b48a699e1404f86cedede6efe7891a",
                "branch": "mt3",
                "formatted_date": "October 05, 2012 01:24 PM",
                "date": "2012-10-05 13:24:31 -0700",
                "message": "Adjusted log time format to indicate local time.",
                "repo_name": "anweb"
            }
        }

        service = Service(**service_data)
        diff = release.diff_service_and_release(service)

        self.assertEqual(diff['changed_packages']['redis']['release_version'], '2.6.2')
        self.assertEqual(diff['changed_packages']['redis']['service_version'], '2.2.2')

    def test_diff_service_and_release_from_files_from_txtasvc(self):
        # Create the service
        current_dir = os.path.dirname(__file__)
        dict_file = open(current_dir + '/test_release_service_service_txtasvc.json')
        service_data = json.loads(dict_file.read())
        service = Service(**service_data)
        dict_file.close()

        # Create the dict data
        current_dir = os.path.dirname(__file__)
        dict_file = open(current_dir + '/test_release_service_dict_txtasvc.json')
        dict_data = json.loads(dict_file.read())
        dict_file.close()

        selected_release = Release.build_release_on_the_fly(dict_data, service)

        diff = selected_release.diff_service_and_release(service)

        self.assertEqual(len(diff['packages_to_subtract'].keys()), 0)
        self.assertEqual(len(diff['packages_to_add'].keys()), 0)

        for name, package_diff_dict in diff['changed_packages'].iteritems():
            self.assertTrue(name in ['redis', 'textanalysis'])
            self.assertTrue(package_diff_dict['release_version'] in ['2.0.0', '0.3.37-master'])


if __name__ == '__main__':
    unittest.main()
