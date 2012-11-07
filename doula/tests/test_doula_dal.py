from doula.cache import Redis
from doula.config import Config
from doula.models.model_factory import ModelFactory
from doula.models.doula_dal import DoulaDAL
import logging
import unittest

log = logging.getLogger('doula')


class TestDoulaDAL(unittest.TestCase):

    def setUp(self):
        Redis.env = 'dev'
        self.redis = Redis.get_instance()
        self.redis.flushdb()
        self.mf = ModelFactory()
        self.dd = DoulaDAL()

        settings = {}
        Config.load_config(settings)

    def tearDown(self):
        pass

    #######################################
    # Build Site and Services From Bambinos
    #######################################

    def test_update_site_and_service_models(self):
        pass

    def test_delete_site_from_cache(self):
        pass

    #############################################
    # Pull the Site or Service Objects From Cache
    #############################################

    def test_get_all_sites(self):
        pass

    def test_find_site_by_name(self):
        pass

    def test_find_service_by_name(self):
        # test_find_service_by_name(self, site_name, service_name):
        pass

    #############################
    # Bambino Register/Unregister
    #############################

    def test_register_node(self):
        node = {
            "url": "http://5.5.0.66:6542",
            "ip": "5.5.0.66",
            "name": "mt1",
            "site": "mt1"
        }

        self.dd.register_node(node)
        registered_site = self.dd.get_registered_site('mt1')

        self.assertEqual(registered_site['name'], 'mt1')

    def test_unregister_node(self):
        pass

    def test_save_registered_site(self):
        pass

    def test_get_registered_site(self):
        pass

    def test_get_registered_site_redis_key(self):
        pass

    #######################
    # Utility Functions
    #######################

    def test_get_all_bambino_ips(self):
        pass

    def test_list_of_sites_and_services(self):
        pass

    def test_get_all_registered_sites(self):
        pass

    def test_get_all_registered_site_names(self):
        pass

if __name__ == '__main__':
    unittest.main()