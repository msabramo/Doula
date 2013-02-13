import simplejson as json
import unittest
import uuid
from mock import call
from mock import Mock
from mock import patch
from doula.cache import Redis
from doula.queue import Queue
from doula.queue import add_result
from doula.queue import add_failure
from doula.config import Config


class QueueTests(unittest.TestCase):
    def setUp(self):
        settings = {}
        Config.load_config(settings)
        Redis.env = 'dev'
        self.redis = Redis.get_instance()

        self.queue = Queue()
        self.queue.redis.flushdb()

    def test_is_maintenance_job(self):
        self.assertTrue(self.queue.is_maintenance_job('cleanup_queue'))
        self.assertFalse(self.queue.is_maintenance_job('bad'))

    def test_is_standard_job(self):
        self.assertTrue(self.queue.is_standard_job('build_new_package'))
        self.assertFalse(self.queue.is_standard_job('bad'))

    def test_save_job(self):
        new_job_dict = {
            'id': 1,
            'status': 'queued',
            'job_type': 'build_new_package'
        }

        rslt = self.queue.save_job(new_job_dict)
        self.assertEqual(new_job_dict['id'], rslt['id'])

    def test_remove(self):
        new_job_dict = {
            'id': '1',
            'status': 'queued',
            'job_type': 'build_new_package'
        }

        rslt = self.queue.save_job(new_job_dict)

        self.queue.remove('1')

        job_queue_key = self.queue._job_queue_key()
        all_jobs = self.redis.hgetall(job_queue_key)
        self.assertEqual(len(all_jobs.keys()), 0)

    def test_find_jobs(self):
        job = {'job_type': 'build_new_package', 'status': 'complete'}

        self._add_job(job.copy())
        self._add_job(job.copy())
        self._add_job(job.copy())

        job_dict_query = {
            'job_type': ['build_new_package']
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 3)

    def test_find_jobs_filter_by_job_type(self):
        self._add_job({'job_type': 'build_new_package'})
        self._add_job({'job_type': 'cycle_service'})
        self._add_job({'job_type': 'build_new_package'})

        job_dict_query = {
            'job_type': ['build_new_package']
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 2)

    def test_find_jobs_filter_by_site(self):
        self._add_job({'job_type': 'build_new_package', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'cycle_service', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'build_new_package', 'site': 'mt2', 'service': 'anweb'})

        job_dict_query = {
            'site': 'mt2'
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 1)

    def test_find_jobs_filter_by_service(self):
        self._add_job({'job_type': 'build_new_package', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'cycle_service', 'site': 'mt3', 'service': 'anonweb'})
        self._add_job({'job_type': 'build_new_package', 'site': 'mt2', 'service': 'anweb'})

        job_dict_query = {
            'service': 'anweb'
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 2)

    def test_find_jobs_filter_by_site(self):
        self._add_job({'job_type': 'build_new_package', 'site': 'mt3'})
        self._add_job({'job_type': 'cycle_service', 'site': 'mt3'})
        self._add_job({'job_type': 'build_new_package', 'site': 'mt2'})

        job_dict_query = {
            'site': 'mt2',
            'service': 'anweb'
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 0)

    def test_find_jobs_filter_by_site_and_service(self):
        self._add_job({'job_type': 'build_new_package', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'cycle_service', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'build_new_package', 'site': 'mt2', 'service': 'anweb'})

        job_dict_query = {
            'site': 'mt3',
            'service': 'anweb',
            'job_type': ['cycle_service', 'release_service', 'build_new_package']
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 2)

    def test_find_jobs_filter_by_job_type_solo(self):
        self._add_job({'job_type': 'build_new_package', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'cycle_service', 'site': 'mt3', 'service': 'anweb'})
        self._add_job({'job_type': 'build_new_package', 'site': 'mt3', 'service': 'anweb'})

        job_dict_query = {
            'job_type': ['build_new_package']
        }

        found_jobs = self.queue.find_jobs(job_dict_query)

        self.assertEqual(len(found_jobs), 2)

    def _add_job(self, new_job_dict={}):
        job_dict = {
            'id': uuid.uuid1().hex,
            'status': 'queued',
            'job_type': 'build_new_package'
        }

        job_dict.update(new_job_dict)

        self.queue.save_job(job_dict)



if __name__ == '__main__':
    unittest.main()