import unittest
from doula.queue import Queue
from doula.queue import base_dicts


class QueueTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_this(self):
        q = Queue()
        job_dict = base_dicts['push_to_cheeseprism']
        job_dict['service'] = 'dummycode'
        job_dict['job_type'] = 'push_to_cheeseprism'
        job_dict['version'] = '0.0.4'
        q.this(job_dict)

    # def test_get(self):
    #     q = Queue()
    #     job_dict = base_dicts['push_to_cheeseprism']
    #     types = ['push_to_cheeseprism',
    #              'push_to_cheeseprism',
    #              'cycle_services']
    #     job_dict['service'] = 'dummycode'
    #     for _type in types:
    #         job_dict['job_type'] = _type
    #         q.this(job_dict)

    #     jobs = q.get({'job_type': 'push_to_cheeseprism'})

    #     self.assertTrue(len(jobs) == 2)

