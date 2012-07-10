import json
import unittest
import doula.queue

from retools.queue import Job
from mock import call
from mock import Mock
from mock import patch
from mockredis import MockRedis

from doula.queue import default_queue_name
from doula.queue import common_dict
from doula.queue import base_dicts
from doula.queue import keys
from doula.queue import get_jobs
from doula.queue import get_job
from doula.queue import pop_job
from doula.queue import save
from doula.queue import update
from doula.queue import Queue
from doula.queue import add_result
from doula.queue import add_failure


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.k = keys()
        doula.queue.rdb = self.rdb = MockRedis()

    def tearDown(self):
        self.rdb.flushdb()

    def _test_job_dict(self, _type):
        return base_dicts[_type]

    def _add_job(self, id):
        push_to_cheeseprism = self._test_job_dict('push_to_cheeseprism')
        push_to_cheeseprism['id'] = id
        self.rdb.sadd(self.k['jobs'], json.dumps(push_to_cheeseprism))
        return push_to_cheeseprism

    def test_keys(self):
        self.assertIn('jobs', keys())

    def test_get_jobs(self):
        k = keys()
        for i in range(5):
            push_to_cheeseprism = base_dicts['push_to_cheeseprism']
            push_to_cheeseprism['id'] = i
            self.rdb.sadd(k['jobs'], json.dumps(push_to_cheeseprism))
        jobs = get_jobs()

        self.assertEqual(len(jobs), 5)

    def test_get_job(self):
        add_job = self._add_job(1)
        job = get_job(1)

        self.assertEqual(add_job, job)

    def test_pop_job(self):
        add_job = self._add_job(1)

        p = self.rdb.pipeline()
        job = pop_job(p, 1)
        p.execute()

        self.assertEqual(add_job, job)
        jobs = self.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 0)

    def test_pop_job_none(self):
        self._add_job(1)

        p = self.rdb.pipeline()
        job = pop_job(p, 2)
        p.execute()

        self.assertEqual(job, None)
        jobs = self.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 1)

    def test_save(self):
        p = self.rdb.pipeline()
        save(p, {'id': 1, 'job_type': 'push_to_cheeseprism'})
        p.execute()

        jobs = self.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 1)
        job = self.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['id'], 1)

    def test_update(self):
        self._add_job(1)

        p = self.rdb.pipeline()
        update(p, {'id': 1, 'status': 'complete'})
        p.execute()

        jobs = self.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 1)
        job = self.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['status'], 'complete')

    def test_update_no_id(self):
        p = self.rdb.pipeline()

        self.assertRaises(Exception, update, p, {})

    def test_update_not_in_redis(self):
        p = self.rdb.pipeline()
        result = update(p, {'id': 2, 'status': 'complete'})
        p.execute()

        self.assertEqual(result, False)

    def test_queue_init(self):
        queue = Queue()
        self.assertIn('job_postrun', queue.qm.global_events)
        self.assertIn('job_failure', queue.qm.global_events)

    @patch('doula.queue.time.time')
    def test_queue_this_push(self, time):
        time.return_value = 0
        queue = Queue()
        queue.qm.enqueue = Mock()
        queue.qm.enqueue.return_value = '234hisadf93uq93254ijfsad93'

        id = queue.this({'job_type': 'push_to_cheeseprism'})
        expected = [call('doula.jobs:push_to_cheeseprism', job_dict={'status': 'queued',
                                                                     'remote': '',
                                                                     'time_started': 0,
                                                                     'service': '',
                                                                     'job_type': 'push_to_cheeseprism',
                                                                     'site': '',
                                                                     'version': '',
                                                                     'branch': 'master',
                                                                     'id': '234hisadf93uq93254ijfsad93',
                                                                     'exc': ''})]
        self.assertEqual(queue.qm.enqueue.mock_calls, expected)
        self.assertEqual(id, '234hisadf93uq93254ijfsad93')

    @patch('doula.queue.time.time')
    def test_queue_this_cycle(self, time):
        time.return_value = 0
        queue = Queue()
        queue.qm.enqueue = Mock()
        queue.qm.enqueue.return_value = '234hisadf93uq93254ijfsad93'

        id = queue.this({'job_type': 'cycle_services'})
        expected = [call('doula.jobs:cycle_services', job_dict={'status': 'queued',
                                                                'time_started': 0,
                                                                'service': '',
                                                                'job_type': 'cycle_services',
                                                                'site': '',
                                                                'id': '234hisadf93uq93254ijfsad93',
                                                                'exc': ''})]
        self.assertEqual(queue.qm.enqueue.mock_calls, expected)
        self.assertEqual(id, '234hisadf93uq93254ijfsad93')

    def test_queue_this_wrong_job_type(self):
        queue = Queue()
        id = queue.this({'job_type': 'asdf'})
        self.assertTrue(isinstance(id, Exception))

    def test_queue_this_none_jobtype(self):
        queue = Queue()
        id = queue.this({})
        self.assertTrue(isinstance(id, Exception))

    def test_queue_get(self):
        queue = Queue()
        id = queue.this({'job_type': 'push_to_cheeseprism'})
        queue.this({'job_type': 'push_to_cheeseprism'})

        jobs = queue.get({'id': id, 'blah': 'key'})
        self.assertEqual(jobs[0]['job_type'], 'push_to_cheeseprism')

        jobs = queue.get({'job_type': 'push_to_cheeseprism'})
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['job_type'], 'push_to_cheeseprism')

    def test_add_result_subscriber(self):
        k = keys()
        retools_job = Mock()
        retools_job.job_id = 0

        job_dict = common_dict
        job_dict['id'] = 0
        job_dict['status'] = 'queued'
        self.rdb.sadd(k['jobs'], json.dumps(job_dict))

        add_result(job=retools_job)

        job = self.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['status'], 'complete')

    def test_add_failure_subscriber(self):
        k = keys()
        retools_job = Mock()
        retools_job.job_id = 0

        job_dict = common_dict
        job_dict['id'] = 0
        job_dict['status'] = 'queued'
        self.rdb.sadd(k['jobs'], json.dumps(job_dict))

        add_failure(job=retools_job, exc=Exception('This is an exception!'))

        job = self.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['status'], 'failed')
        self.assertIsNot(job['exc'], None)
