import unittest

from doula.models.audit import Audit
from doula.cache import Cache

class AuditTests(unittest.TestCase):
    def setUp(self):
        Cache.env = 'dev'
        self.cache = Cache.cache()
        self.cache.flushall()

    def tearDown(self):
        pass

    def test_log_action(self):
        audit = Audit()
        audit.log_action('env_name', 'app_name', 'deploy', 'anonymous')
        
        logs = audit.get_app_logs('env_name', 'app_name')
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['user'], 'anonymous')
    

if __name__ == '__main__':
    unittest.main()