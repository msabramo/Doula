from doula.config import Config
from doula.models.webhook import WebHook
from doula.github import *
import unittest
import json


class GithubHooksTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.config.org': 'config',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69',
            'doula.github.webhook.url':'http://doula.corp.surveymonkey.com/webhook/callbacks'
        }

        Config.load_config(settings)

    def tearDown(self):
        pass


    def test_parse_payload(self):
        wh = WebHook()
        wh.parse_payload(json.loads(self.basic_payload()))

        self.assertEqual(wh.repo, 'smtemplates')
        self.assertEqual(wh.org, 'devmonkeys')
        self.assertEqual(wh.branch, 'master')
        self.assertEqual(wh.sha1, '41b230b2036954e46a68e6ba8944873aa4d2991b')
        self.assertEqual(wh.compare_url, 'http://code.corp.surveymonkey.com/devmonkeys/smtemplates/compare/7f2ffd0e0fd4...41b230b20369')


    def basic_payload(self):
        return """
            {
                "after": "41b230b2036954e46a68e6ba8944873aa4d2991b",
                "before": "7f2ffd0e0fd4331840028c69cdc9b661a9679d33",
                "commits": [
                    {
                        "added": [],
                        "author": {
                            "email": "alexv@surveymonkey.com",
                            "name": "alexv",
                            "username": "alexv"
                        },
                        "committer": {
                            "email": "alexv@surveymonkey.com",
                            "name": "alexv",
                            "username": "alexv"
                        },
                        "distinct": true,
                        "id": "6b291499271d20e6d70ece8e9e28e47b27221843",
                        "message": "bump version",
                        "modified": [
                            "setup.py"
                        ],
                        "removed": [],
                        "timestamp": "2013-01-16T16:42:41-08:00",
                        "url": "http://code.corp.surveymonkey.com/devmonkeys/smtemplates/commit/6b291499271d20e6d70ece8e9e28e47b27221843"
                    },
                    {
                        "added": [],
                        "author": {
                            "email": "alexv@surveymonkey.com",
                            "name": "alexv",
                            "username": "alexv"
                        },
                        "committer": {
                            "email": "alexv@surveymonkey.com",
                            "name": "alexv",
                            "username": "alexv"
                        },
                        "distinct": true,
                        "id": "d76db68ae0f5b114c2db4817272460ed7b9784d7",
                        "message": "bump version",
                        "modified": [
                            "setup.py"
                        ],
                        "removed": [],
                        "timestamp": "2013-01-17T12:24:42-08:00",
                        "url": "http://code.corp.surveymonkey.com/devmonkeys/smtemplates/commit/d76db68ae0f5b114c2db4817272460ed7b9784d7"
                    },
                    {
                        "added": [],
                        "author": {
                            "email": "alexv@surveymonkey.com",
                            "name": "alexv",
                            "username": "alexv"
                        },
                        "committer": {
                            "email": "alexv@surveymonkey.com",
                            "name": "alexv",
                            "username": "alexv"
                        },
                        "distinct": true,
                        "id": "41b230b2036954e46a68e6ba8944873aa4d2991b",
                        "message": "bump version",
                        "modified": [
                            "setup.py"
                        ],
                        "removed": [],
                        "timestamp": "2013-01-17T14:34:56-08:00",
                        "url": "http://code.corp.surveymonkey.com/devmonkeys/smtemplates/commit/41b230b2036954e46a68e6ba8944873aa4d2991b"
                    }
                ],
                "compare": "http://code.corp.surveymonkey.com/devmonkeys/smtemplates/compare/7f2ffd0e0fd4...41b230b20369",
                "created": false,
                "deleted": false,
                "forced": false,
                "head_commit": {
                    "added": [],
                    "author": {
                        "email": "alexv@surveymonkey.com",
                        "name": "alexv",
                        "username": "alexv"
                    },
                    "committer": {
                        "email": "alexv@surveymonkey.com",
                        "name": "alexv",
                        "username": "alexv"
                    },
                    "distinct": true,
                    "id": "41b230b2036954e46a68e6ba8944873aa4d2991b",
                    "message": "bump version",
                    "modified": [
                        "setup.py"
                    ],
                    "removed": [],
                    "timestamp": "2013-01-17T14:34:56-08:00",
                    "url": "http://code.corp.surveymonkey.com/devmonkeys/smtemplates/commit/41b230b2036954e46a68e6ba8944873aa4d2991b"
                },
                "pusher": {
                    "name": "none"
                },
                "ref": "refs/heads/master",
                "repository": {
                    "created_at": "2011-09-19T06:58:59-07:00",
                    "fork": false,
                    "forks": 2,
                    "has_downloads": true,
                    "has_issues": false,
                    "has_wiki": true,
                    "language": "JavaScript",
                    "name": "smtemplates",
                    "open_issues": 0,
                    "organization": "devmonkeys",
                    "owner": {
                        "email": "devmonkeys@surveymonkey.com",
                        "name": "devmonkeys"
                    },
                    "private": false,
                    "pushed_at": "2013-01-17T15:44:40-08:00",
                    "size": 9232,
                    "stargazers": 5,
                    "url": "http://code.corp.surveymonkey.com/devmonkeys/smtemplates",
                    "watchers": 5
                }
            }
        """

if __name__ == '__main__':
    unittest.main()
