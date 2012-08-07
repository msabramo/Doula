from doula.cache import Cache
from doula.views.helpers import (
    not_found,
    log_error
)
from doula.views.index import bambino_register
from pyramid import testing
import json
import unittest


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
            'url': 'http://127.0.0.1:6542'
        }

        request.POST['action'] = 'register'
        request.POST['node'] = json.dumps(node)
        result = bambino_register(request)
        self.assertEqual(result['success'], 'true')

    def test_helpers_not_found(self):
        request = testing.DummyRequest()
        request.exception = Exception("Exception")

        response = not_found(request)
        self.assertIn('msg', response)
        self.assertEqual(response['msg'], "Exception")
        self.assertIn('config', response)

    def test_helpers_log_error(self):
        pass

if __name__ == '__main__':
    unittest.main()
