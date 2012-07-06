import unittest
from doula.cache import Cache
from doula.models.sites_dal import SiteDAL


class TestSitesDAL(unittest.TestCase):
    def setUp(self):
        Cache.env = 'dev'
        Cache.clear_cache()
        self.cache = Cache.cache()

    def test_cache_store(self):
        # Just make sure we get a valid cache store from cache
        self.cache.set('key', 'value')
        self.assertEqual(self.cache.get('key'), 'value')

    def test_register_node(self):
        site = 'site1'

        node1 = {
            'name': 'node1',
            'site': site,
            'url': 'http://node1'
        }

        node2 = {
            'name': 'node2',
            'site': site,
            'url': 'http://node2'
        }

        SiteDAL.register_node(node1)
        SiteDAL.register_node(node2)

        self.assertEqual(len(SiteDAL.nodes(site).keys()), 2)

        node3 = {
            'name': 'node3',
            'site': site,
            'url': 'http://node3'
        }

        SiteDAL.register_node(node3)

        self.assertEqual(len(SiteDAL.nodes(site).keys()), 3)

    def test_register_node_two(self):
        # Make sure we don't return an unknown site
        nodes = SiteDAL.nodes('unknown site')
        self.assertEqual(len(nodes), 0)

    def test_unregister_node(self):
        node1 = {
            'name': 'node1',
            'site': 'site1',
            'url': 'http://node1'
        }

        SiteDAL.register_node(node1)

        self.assertEqual(len(SiteDAL.nodes('site1').keys()), 1)

        SiteDAL.unregister_node(node1)
        self.assertEqual(len(SiteDAL.nodes('site1').keys()), 0)

        sites = SiteDAL.get_sites()
        self.assertEqual(len(sites.keys()), 0)

    def test_all_site_keys(self):
        node = {
            'name': 'node1',
            'site': 'site1',
            'url': 'http://node1'
        }

        SiteDAL.register_node(node)
        keys = SiteDAL._all_site_keys()

        self.assertEqual(keys[0], 'site:site1')

    def test_get_sites(self):
        # Get Site objects array, [Site, Site, Site...]
        self._register_node()

        sites = SiteDAL.get_sites()
        self.assertEqual(len(sites), 1)
        self.assertEqual(len(sites['site1'].nodes.keys()), 1)

    def _register_node(self):
        node = {
            'name': 'node1',
            'site': 'site1',
            'url': 'http://node1'
        }

        SiteDAL.register_node(node)

if __name__ == '__main__':
    unittest.main()
