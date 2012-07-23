import os
import unittest
import time
from mock import patch
from mockredis import MockRedis
from datetime import datetime
from doula.queue import Queue
from doula.jobs import cleanup_queue


class JobTests(unittest.TestCase):
    @patch('doula.queue.redis.Redis', new=MockRedis)
    def setUp(self):
        self.queue = Queue()
        self.k = self.queue._keys()

    @patch('doula.queue.redis.Redis', new=MockRedis)
    def tearDown(self):
        self.queue.rdb.flushdb()

    @patch('doula.jobs.Queue')
    def test_cleanup_queue(self, Queue):
        Queue.return_value = self.queue
        now = datetime.now()
        now = time.mktime(now.timetuple())

        old_complete_time = now - 7400
        old_failed_time = now - 14600
        new_time = now - 200

        job_dicts = [{
            'id': '1',
            'status': 'complete',
            'time_started': old_complete_time
        },
        {
            'id': '2',
            'status': 'complete',
            'time_started': new_time
        },
        {
            'id': '3',
            'status': 'failed',
            'time_started': old_failed_time
        },
        {
            'id': '4',
            'status': 'failed',
            'time_started': new_time
        }]

        p = self.queue.rdb.pipeline()
        for job_dict in job_dicts:
            self.queue._save(p, job_dict)
        p.execute()

        for id in range(1, 4):
            FILE = open(os.path.join('/var/log/doula', str(id) + '.log'), "w")
            FILE.close()

        cleanup_queue(job_dict={'id': '6'})

        persisted_jobs = self.queue._get_jobs()
        ids = [job['id'] for job in persisted_jobs]
        self.assertNotIn('1', ids)
        self.assertIn('2', ids)
        self.assertNotIn('3', ids)
        self.assertIn('4', ids)
