from doula.cache import Redis
from doula.views.index import bambino_register
from pyramid import testing
import simplejson as json
import unittest


class ViewTests(unittest.TestCase):
    def setUp(self):
        Redis.env = 'dev'
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


if __name__ == '__main__':
    unittest.main()
