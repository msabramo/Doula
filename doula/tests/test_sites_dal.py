import unittest
from doula.cache import Redis
from doula.config import Config
from doula.models.doula_dal import DoulaDAL


class TestSitesDAL(unittest.TestCase):
    def setUp(self):
        Redis.env = 'dev'
        self.redis = Redis.get_instance()
        self.redis.flushdb()
        self.dd = DoulaDAL()

        settings = {}
        Config.load_config(settings)

    def test_register_node(self):
        site = 'site1'

        node1 = {
            'name': 'node1',
            'site': site,
            'url': 'http://node1',
            'ip': '127.0.0.1'
        }

        node2 = {
            'name': 'node2',
            'site': site,
            'url': 'http://node2',
            'ip': '127.0.0.1'
        }

        self.dd.register_node(node1)
        self.dd.register_node(node2)

        self.assertEqual(len(self.dd.nodes(site).keys()), 2)

        node3 = {
            'name': 'node3',
            'site': site,
            'url': 'http://node3',
            'ip': '127.0.0.1'
        }

        self.dd.register_node(node3)

        self.assertEqual(len(self.dd.nodes(site).keys()), 3)

    def test_register_node_two(self):
        # Make sure we don't return an unknown site
        nodes = self.dd.nodes('unknown site')
        self.assertEqual(len(nodes), 0)

    def test_unregister_node(self):
        node1 = {
            'name': 'node1',
            'site': 'site1',
            'url': 'http://node1',
            'ip': '127.0.0.1'
        }

        self.dd.register_node(node1)

        self.assertEqual(len(self.dd.nodes('site1').keys()), 1)

        self.dd.unregister_node(node1)
        self.assertEqual(len(self.dd.nodes('site1').keys()), 0)

        sites = self.dd.get_sites()
        self.assertEqual(len(sites.keys()), 0)

    def test_get_all_registered_site_names(self):
        node = {
            'name': 'node1',
            'site': 'site1',
            'url': 'http://node1',
            'ip': '127.0.0.1'
        }

        self.dd.register_node(node)
        keys = self.dd._get_all_registered_site_names()

        self.assertEqual(keys[0], 'site1')

    def test_get_sites(self):
        # Get Site objects array, [Site, Site, Site...]
        self._register_node()

        sites = self.dd.get_sites()
        self.assertEqual(len(sites), 1)
        self.assertEqual(len(sites['site1'].nodes.keys()), 1)

    def _register_node(self):
        node = {
            'name': 'node1',
            'site': 'site1',
            'url': 'http://node1',
            'ip': '127.0.0.1'
        }

        self.dd.register_node(node)

if __name__ == '__main__':
    unittest.main()
