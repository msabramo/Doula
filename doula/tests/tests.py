import json
import unittest

from pyramid import testing
from doula.views import register
from doula.cache import Cache

class ViewTests(unittest.TestCase):
    def setUp(self):
        Cache.env = 'dev'
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_register(self):
        request = testing.DummyRequest()
        
        node = {
            'name': 'Bambino 1',
            'site': 'Monkey Test One',
            'url' : 'http://127.0.0.1:6542'
        }
        
        request.POST['action'] = 'register'
        request.POST['node'] = json.dumps(node)
        result = register(request)
        self.assertEqual(result['success'], 'true')
    

if __name__ == '__main__':
    unittest.main()
