import json
import unittest
import uuid

from mock import call
from mock import Mock
from mock import patch
from mockredis import MockRedis

from doula.queue import Queue
from doula.queue import add_result
from doula.queue import add_failure


@patch('doula.queue.redis.Redis', new=MockRedis)
class QueueTests(unittest.TestCase):
    @patch('doula.queue.redis.Redis', new=MockRedis)
    def setUp(self):
        self.queue = Queue()
        self.k = self.queue._keys()

    @patch('doula.queue.redis.Redis', new=MockRedis)
    def tearDown(self):
        self.queue.rdb.flushdb()

    def _test_job_dict(self, _type):
        return self.queue.base_dicts[_type]

    def _add_job(self, id):
        rdb = self.queue.rdb

        # Create test "Job" dict, with a specific id
        push_to_cheeseprism = self._test_job_dict('push_to_cheeseprism')
        push_to_cheeseprism['id'] = id

        # Add to redis, and return the "Job" dict
        rdb.sadd(self.k['jobs'], json.dumps(push_to_cheeseprism))
        return push_to_cheeseprism

    def test_keys(self):
        self.assertIn('jobs', self.queue._keys())

    def test_get_jobs(self):
        # Create 5 test jobs
        for i in range(5):
            self._add_job(i)
        jobs = self.queue._get_jobs()

        self.assertEqual(len(jobs), 5)

    def test_get_job(self):
        add_job = self._add_job(1)
        job = self.queue._get_job(1)

        self.assertEqual(add_job, job)

    def test_pop_job(self):
        add_job = self._add_job(1)

        p = self.queue.rdb.pipeline()
        job = self.queue._pop_job(p, 1)
        p.execute()

        self.assertEqual(add_job, job)
        jobs = self.queue.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 0)

    def test_pop_job_none(self):
        self._add_job(1)

        p = self.queue.rdb.pipeline()
        job = self.queue._pop_job(p, 2)
        p.execute()

        self.assertEqual(job, None)
        jobs = self.queue.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 1)

    def test_save(self):
        p = self.queue.rdb.pipeline()
        self.queue._save(p, {'id': 1, 'job_type': 'push_to_cheeseprism'})
        p.execute()

        jobs = self.queue.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 1)
        job = self.queue.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['id'], 1)

    def test_update(self):
        self._add_job(1)

        p = self.queue.rdb.pipeline()
        self.queue._update(p, {'id': 1, 'status': 'complete'})
        p.execute()

        jobs = self.queue.rdb.smembers(self.k['jobs'])
        self.assertEqual(len(jobs), 1)
        job = self.queue.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['status'], 'complete')

    def test_update_not_in_redis(self):
        p = self.queue.rdb.pipeline()
        result = self.queue._update(p, {'id': 2, 'status': 'complete'})
        p.execute()

        self.assertEqual(result, False)

    def test_pub_update_no_id(self):
        p = self.queue.rdb.pipeline()

        self.assertRaises(Exception, self.queue.update, p, {})

    def test_queue_init(self):
        self.assertIn('job_postrun', self.queue.qm.global_events)
        self.assertIn('job_failure', self.queue.qm.global_events)

    @patch('doula.queue.time.time')
    def test_queue_this_push(self, time):
        time.return_value = 0
        qm = self.queue.qm
        qm.enqueue = Mock()
        qm.enqueue.return_value = '234hisadf93uq93254ijfsad93'

        id = self.queue.this({'job_type': 'push_to_cheeseprism'})
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
        self.assertEqual(qm.enqueue.mock_calls, expected)
        self.assertEqual(id, '234hisadf93uq93254ijfsad93')

    @patch('doula.queue.time.time')
    def test_queue_this_cycle(self, time):
        time.return_value = 0
        qm = self.queue.qm
        qm.enqueue = Mock()
        qm.enqueue.return_value = '234hisadf93uq93254ijfsad93'

        id = self.queue.this({'job_type': 'cycle_services'})
        expected = [call('doula.jobs:cycle_services', job_dict={'status': 'queued',
                                                                'time_started': 0,
                                                                'service': '',
                                                                'job_type': 'cycle_services',
                                                                'site': '',
                                                                'id': '234hisadf93uq93254ijfsad93',
                                                                'exc': ''})]
        self.assertEqual(qm.enqueue.mock_calls, expected)
        self.assertEqual(id, '234hisadf93uq93254ijfsad93')

    def test_queue_this_wrong_job_type(self):
        id = self.queue.this({'job_type': 'asdf'})
        self.assertTrue(isinstance(id, Exception))

    def test_queue_this_none_jobtype(self):
        id = self.queue.this({})
        self.assertTrue(isinstance(id, Exception))

    def test_queue_get(self):
        # Have it return a random hex string as an id
        qm = self.queue.qm
        qm.enqueue = Mock(side_effect=lambda *args, **kwargs: uuid.uuid4().hex)

        id = self.queue.this({'job_type': 'push_to_cheeseprism'})
        self.queue.this({'job_type': 'push_to_cheeseprism'})
        self.queue.this({'job_type': 'cycle_services'})

        jobs = self.queue.get({'id': id, 'blah': 'key'})
        self.assertEqual(jobs[0]['job_type'], 'push_to_cheeseprism')

        jobs = self.queue.get({'job_type': 'push_to_cheeseprism'})
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['job_type'], 'push_to_cheeseprism')

    def test_add_result_subscriber(self):
        retools_job = Mock()
        retools_job.job_id = uuid.uuid4().hex

        job_dict = self.queue.common_dict
        job_dict['id'] = retools_job.job_id
        job_dict['status'] = 'queued'
        self.queue.rdb.sadd(self.k['jobs'], json.dumps(job_dict))

        add_result(job=retools_job)

        job = self.queue.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['status'], 'complete')

    def test_add_failure_subscriber(self):
        retools_job = Mock()
        retools_job.job_id = 0

        job_dict = self.queue.common_dict
        job_dict['id'] = 0
        job_dict['status'] = 'queued'
        self.queue.rdb.sadd(self.k['jobs'], json.dumps(job_dict))

        add_failure(job=retools_job, exc=Exception('This is an exception!'))

        job = self.queue.rdb.srandmember(self.k['jobs'])
        job = json.loads(job)
        self.assertEqual(job['status'], 'failed')
        self.assertIsNot(job['exc'], None)
