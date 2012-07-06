import os
import unittest
from mock import patch
from mock import call
from doula.cache import Cache
from doula.models.sites_dal import SiteDAL
from doula.models.package import Package


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


class PackageTests(unittest.TestCase):
    def setUp(self):
        pass

    def testDown(self):
        pass

    def make_one(self):
        return Package("dummycode")

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
