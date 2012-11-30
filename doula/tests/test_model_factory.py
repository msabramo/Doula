from doula.config import Config
from doula.models.model_factory import ModelFactory
from doula.models.node import Node
from doula.models.site import Site
from mock import MagicMock
import unittest


class ModelFactoryTests(unittest.TestCase):

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

        self.service_as_dict = {
            "current_branch_app": "mt3",
            "change_count_app": 0,
            "change_count_config": 0,
            "remote": "git@code.corp.surveymonkey.com:AppEnv/anweb.git",
            "name": "anweb",
            "tags": [
                {
                    "date": 1334013665,
                    "message": "all the kings horses",
                    "name": "x.2"
                }
            ],
            "is_dirty_app": True,
            "last_tag_message": "all the kings horses",
            "is_dirty_config": True,
            "status": "uncommitted_changes",
            "last_tag_config": "x.2",
            "changed_files": [
                "bin/activate.csh"
            ],
            "last_tag_app": "x.2",
            "packages": {
                "repoze.lru": {
                    "version": "0.3",
                    "name": "repoze.lru"
                },
                "pyramid": {
                    "version": "1.2.7",
                    "name": "pyramid"
                }
            },
            "config": {
                "short_sha1": "\"5f775a3\""
            },
            "current_branch_config": "mt3",
            "supervisor_service_names": []
        }

        self.nodes_as_dicts = {
            "mtclone-pyweb01": {
                "url": "http://192.168.4.13:6666",
                "ip": "192.168.4.13",
                "name": "mtclone-pyweb01",
                "site": "mtclone"
            }
        }

        self.mf = ModelFactory()

    def tearDown(self):
        pass

    def test__build_nodes_from_dicts(self):
        nodes = self.mf._build_nodes_from_bambino_dicts(self.nodes_as_dicts)

        self.assertEqual(nodes['mtclone-pyweb01'].name, 'mtclone-pyweb01')
        self.assertEqual(nodes['mtclone-pyweb01'].site_name, 'mtclone')

    def test__update_or_create_service(self):
        services = {}
        node = Node('mtclone-pyweb01',
                    'mtclone',
                    'http://192.168.4.13:6666',
                    '192.168.4.13')

        service = self.mf._update_or_create_service(services, self.service_as_dict, node)

        self.assertEqual(len(service.nodes.keys()), 1)
        self.assertEqual(service.name, 'anweb')
        self.assertEqual(service.remote, self.service_as_dict['remote'])
        self.assertTrue(service.nodes['mtclone-pyweb01'])

    def test__get_updated_site_services(self):
        # get the site nodes
        node = MagicMock()
        node.name = 'mtclone-pyweb01'
        node.site_name = 'mtclone'
        node.url = 'http://127.0.0.1:6543'
        node.ip = '127.0.0.1'
        node.pull_services_as_dicts.return_value = {'services': [self.service_as_dict]}

        nodes = {
            'mtclone-pyweb01': node
        }

        # build a site without the services
        site = Site('mtclone', status='unknown', nodes=nodes)

        # get the services for the site
        site.services = self.mf._get_updated_site_services(site)

        self.assertEqual(len(site.services.keys()), 1)
        self.assertEqual(site.services['anweb'].name, 'anweb')

    def test_build_site_from_cache(self):
        self.service_as_dict['site_name'] = 'mtclone'

        # when the node comes back from cache it has a 'site_name' attribute
        self.nodes_as_dicts['mtclone-pyweb01']['site_name'] = 'mtclone'
        self.service_as_dict['nodes'] = self.nodes_as_dicts

        site_as_dict = {
            "name": "mtclone",
            "status": "unknown",
            "nodes": self.nodes_as_dicts,
            "services": {
                "anweb": self.service_as_dict
            }
        }

        site = self.mf.build_site_from_cache(site_as_dict)

        self.assertEqual(site.name, 'mtclone')

    def test_build_service_from_cache(self):
        self.service_as_dict['site_name'] = 'mtclone'

        # when the node comes back from cache it has a 'site_name' attribute
        self.nodes_as_dicts['mtclone-pyweb01']['site_name'] = 'mtclone'
        self.service_as_dict['nodes'] = self.nodes_as_dicts

        service = self.mf.build_service_from_cache(self.service_as_dict)

        self.assertEqual(service.name, 'anweb')
        self.assertEqual(len(service.nodes.keys()), 1)


if __name__ == '__main__':
    unittest.main()






