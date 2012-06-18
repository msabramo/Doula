import unittest
from doula.util import pprint
from doula.cache import Cache
from doula.models.sites import Application
from doula.models.sites_dal import SiteDAL
from doula.util import dirify

class TestSitesDAL(unittest.TestCase):
    def setUp(self):
        Cache.env = 'dev'
        self.cache = Cache.cache()
        self.cache.flushall()
    
    def test_save_service_as_deployed(self):
        app = Application('app_name', 'env_name', 'node_name', 'http://0.0.0.0.6542')
        app.status = 'tagged'
        tags = [{'name': 'last tag', 'message': 'last tag message', 'date': '8484848'}]
        app.add_tags_from_dict(tags)
        
        tag = app.get_tag_by_name('last tag')
        app.mark_as_deployed(tag, 'anonymous')
        
        self.assertEqual(app.get_status(), 'deployed')
        
        key = SiteDAL._get_deployed_app_key(app)
        self.assertEqual(key, 'env_name_app_name_deployed')
        
        self.assertTrue(SiteDAL.is_deployed(app, tag))
    

if __name__ == '__main__':
    unittest.main()