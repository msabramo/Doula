from doula.config import Config
from doula.github import *
import unittest


class GithubHooksTests(unittest.TestCase):
    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'AppEnv',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.config.org': 'config',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69'
            'doula.github.webhook.url':'http://doula.corp.surveymonkey.com/webhook/callbacks'
        }

        Config.load_config(settings)

    def tearDown(self):
        pass

    #def test_pull_repo_hooks(self):
        #result = pull_repo_hooks('smtemplates')
        #print result

    #def test_add_hook_to_repo(self):
        #result = add_hook_to_repo('smtemplates')
        #print result

    def test_all_repos_in_org(self):
        result = all_repos_in_org('devmonkeys')
        print result

    #def test_pull_services_for_config_names(self):
        #result = pull_services_for_config_names()

        #self.assertTrue(len(result) > 0)

    #def test_pull_service_configs(self):
        #result = pull_service_configs('billweb')

        #self.assertTrue(result)

    #def test_build_url_to_api(self):
        #url = "%(domain)s and %(token)s and %(name)s"
        #params = {"name": "quezo"}
        #result = build_url_to_api(url, params)

        #expected = "http://api.code.corp.surveymonkey.com and "
        #expected += "17e6642dca429043725ad6a98ce966e5a67eac69 and quezo"

        #self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
