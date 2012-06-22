import unittest
from doula.queue import Queue
from doula.queue import push_to_cheeseprism_dict


class QueueTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_this(self):
        q = Queue()
        job_dict = push_to_cheeseprism_dict
        q.this(job_dict)
