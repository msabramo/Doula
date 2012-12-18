from doula.cache import Redis
from doula.config import Config
from doula.models.release_dal import ReleaseDAL
import unittest


class ReleaseDALTests(unittest.TestCase):
    def setUp(self):
        Redis.env = 'dev'
        self.releaseDAL = ReleaseDAL()

        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
        }

        Config.load_config(settings)

    def testDown(self):
        pass

    def test_next_release(self):
        next = self.releaseDAL.next_release('site_name', 'service_name')

        self.assertEqual(next, 1)

        next = self.releaseDAL.next_release('site_name', 'service_name')
        self.assertEqual(next, 2)

        next = self.releaseDAL.next_release('site_name', 'service_name')
        self.assertEqual(next, 3)

        next = self.releaseDAL.next_release('site_name1', 'service_name1')
        self.assertEqual(next, 1)

    def test_add_manifest(self):
        manifest = {
          "sha1_etc": "abc123",
          "release_number": 15,
          "site": "mt1",
          "service": "anweb",
          "pip_freeze": ["anweb==1.1"],
          "is_rollaback": True,
          "date": "2012-11-10T00:20:03+00:00",
          "commit_message": "",
          "author": "tsabat"
        }

        self.releaseDAL.add_manifest('site_name', 'service_name', manifest)

        manifest = self.releaseDAL.find_manifest_by_release_number('site_name', 'service_name', 15)

        self.assertEqual(manifest['sha1_etc'], 'abc123')

    def test_update_manifest(self):
        manifest = {
          "sha1_etc": "abc123",
          "release_number": 15,
          "site": "mt1",
          "service": "anweb",
          "pip_freeze": ["anweb==1.1"],
          "is_rollaback": True,
          "date": "2012-11-10T00:20:03+00:00",
          "commit_message": "",
          "author": "tsabat"
        }

        self.releaseDAL.add_manifest('site_name', 'service_name', manifest)

        manifest = self.releaseDAL.find_manifest_by_release_number('site_name', 'service_name', 15)

        more_data = {
            'production': True
        }

        self.releaseDAL.update_manifest(manifest, more_data)

        self.assertEqual(manifest['production'], True)

    def test_find_releases_for_service(self):
        manifest = {
          "sha1_etc": "abc123",
          "release_number": 15,
          "site": "mt1",
          "service": "anweb",
          "pip_freeze": ["anweb==1.1"],
          "is_rollaback": True,
          "date": "2012-11-13T18:44:56",
          "commit_message": "first commit message",
          "author": "tsabat"
        }

        self.releaseDAL.add_manifest('mt1', 'anweb', manifest)

        manifest2 = manifest.copy()
        manifest2["release_number"] = 16
        manifest2["commit_message"] = "second commit message"
        self.releaseDAL.add_manifest('mt1', 'anweb', manifest2)

        releases = self.releaseDAL.find_releases_for_service('mt1', 'anweb', 20)

        self.assertEqual(len(releases), 2)
        self.assertEqual(releases[0].sha1_etc, "abc123")

if __name__ == '__main__':
    unittest.main()
