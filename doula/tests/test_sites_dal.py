import unittest
from doula.util import pprint
from doula.cache import Cache
from doula.models.sites import Application
from doula.models.sites_dal import SiteDAL
from doula.util import dirify

class TestSitesDAL(unittest.TestCase):
    def setUp(self):
        self.cache = Cache.cache()
        self.cache.flushall()
    
    def test_save_application_as_deployed(self):
        app = Application('app_name', 'site_name', 'node_name', 'http://0.0.0.0.6542')
        app.status = 'tagged'
        app.last_tag_app = dirify('last tag')
        app.last_tag_message = 'last tag message'
        app.mark_as_deployed()
        
        self.assertEqual(app.get_status(), 'deployed')
        
        sd = SiteDAL()
        key = sd._get_deployed_app_key(app)
        self.assertEqual(key, 'site_name_app_name_deploy_' + app.last_tag_app)
        
        self.assertTrue(sd.is_deployed(app))
    

if __name__ == '__main__':
    unittest.main()