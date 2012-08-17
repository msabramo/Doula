from doula.notifications import send_notification
from retools.queue import QueueManager
import json
import logging
import redis
import time
import traceback
import uuid


class Queue(object):
    """
    This class represents all of Doula's interaction with the queueing
    engine.  The common link between Doula and this class is the
    "Job" dict.  This "Job" dict is of the following format:

    Common for every job:
    {
        id: '',
        user_id: '',
        status: (queued, complete, failed),
        job_type: (push_package|cycle_service)
        site: '',
        service: '',
        time_started: ''
    }

    Push to Cheese Prism
    {
        remote: '', (origin to pull from)
        branch: '', (the branch to pull from)
        version: '', (the version of the package we want to create on cheeseprism)
    }

    Cycle Services
    {

    }

    API:
    ----
    Queue.this(dict)
    - Accepts a "Job" dict, determines the correct job function, and enqueues the job
      function

    Queue.get(dict)
    - Accepts a "Job" dict, queries redis to obtain all of the related jobs, and always
      returns an array of jobs.

    """

    default_queue_name = 'main'

    common_dict = {
        'id': 0,
        'user_id': '',
        'status': '',
        'job_type': '',
        'site': '',
        'service': '',
        'time_started': 0,
        'exc': ''
    }

    push_service_environment_dict = dict({
        'site_name_or_node_ip': '',
        'username': '',
        'email': '',
        'service_name': '',
        'packages': []
    }.items() + common_dict.items())

    push_to_cheeseprism_dict = dict({
        'remote': '',
        'branch': 'master',
        'version': ''
    }.items() + common_dict.items())

    base_dicts = {
        'base': common_dict,
        'push_to_cheeseprism': push_to_cheeseprism_dict,
        'cycle_services': common_dict,
        'pull_cheeseprism_data': common_dict,
        'pull_github_data': common_dict,
        'pull_bambino_data': common_dict,
        'cleanup_queue': common_dict
    }

    def __init__(self):
        # Initialize redis database
        self.rdb = redis.Redis()

        # Initialize the QueueManager
        self.qm = QueueManager(default_queue_name=self.default_queue_name)
        self.qm.subscriber('job_postrun', handler='doula.queue:add_result')
        self.qm.subscriber('job_failure', handler='doula.queue:add_failure')

    def this(self, attrs):
        """
        Enqueues a job onto the retools queue
        """
        job_types = [
            'push_to_cheeseprism',
            'cycle_services',
            'pull_cheeseprism_data',
            'pull_github_data',
            'pull_bambino_data',
            'cleanup_queue']

        if 'job_type' in attrs and attrs['job_type'] in job_types:
            _type = attrs['job_type']
            job_dict = self.base_dicts[_type].copy()
        else:
            return Exception('A valid job type must be specified.')

        for key, val in attrs.items():
            job_dict[key] = val

        # generate unique id
        job_dict['id'] = uuid.uuid1().hex
        job_dict['status'] = 'queued'
        job_dict['time_started'] = time.time()
        job_type = job_dict['job_type']
        p = self.rdb.pipeline()

        self.qm.enqueue('doula.jobs:%s' % job_type, job_dict=job_dict)

        self._save(p, job_dict)
        p.execute()

        return job_dict['id']

    def get(self, job_dict={}):
        """
        Find the jobs that meet criteria sent in the job_dict
        """
        jobs = self._get_jobs()

        # Loop through each criteria, throw out the jobs that don't meet
        for job in list(jobs):
            for k, v in job_dict.items():
                try:
                    if isinstance(v, basestring):
                        if job[k] != v:
                            jobs.remove(job)
                    elif type(v) == list:
                        if not job[k] in v:
                            jobs.remove(job)
                except (KeyError, ValueError):
                    continue

        return jobs

    def update(self, job_dict):
        if not 'id' in job_dict:
            raise Exception('Must pass an id into the update function.')

        p = self.rdb.pipeline()
        job_dict = self._update(p, job_dict)
        p.execute()

        return job_dict

    def remove(self, job_dict_ids):
        if isinstance(job_dict_ids, basestring):
            job_dict_ids = [job_dict_ids]

        p = self.rdb.pipeline()
        self._remove_jobs(p, job_dict_ids)
        p.execute()

    def _keys(self):
        """
        Returns the standard keys for interacting with redis.
        """
        return {
            'jobs': 'doula:jobs:' + self.default_queue_name
        }

    def _get_jobs(self):
        # Combine the two job locations
        k = self._keys()
        jobs_json = self.rdb.smembers(k['jobs'])

        # Created a list of all of the jobs(dict)
        jobs = []

        for job_json in jobs_json:
            job = json.loads(job_json)
            jobs.append(job)

        return jobs

    def _get_job(self, id):
        jobs = self._get_jobs()

        for job in jobs:
            if job['id'] == id:
                return job

    def _pop_job(self, p, id):
        k = self._keys()
        jobs = self._get_jobs()

        for job in jobs:
            if job['id'] == id:
                p.srem(k['jobs'], json.dumps(job, sort_keys=True))
                return job

        return None

    def _remove_jobs(self, p, ids):
        k = self._keys()
        jobs = self._get_jobs()

        for job in jobs:
            if job['id'] in ids:
                p.srem(k['jobs'], json.dumps(job, sort_keys=True))

    def _save(self, p, attrs):
        """
        Given a complete "Job" dict, saves it
        """
        k = self._keys()
        p.sadd(k['jobs'], json.dumps(attrs, sort_keys=True))

    def _update(self, p, attrs):
        """
        Updates a specific "Job" dict, must be given an id
        """
        k = self._keys()
        job_dict = self._pop_job(p, attrs['id'])

        if job_dict:
            for key, val in attrs.items():
                job_dict[key] = val

            p.sadd(k['jobs'], json.dumps(job_dict, sort_keys=True))

            return job_dict
        else:
            return False


#
# Retools Subscribers
#
def add_result(job=None, result=None):
    """
    Subscriber that gets called right after the job gets run, and is successful.
    """
    queue = Queue()
    job_dict = queue.update({'id': job.kwargs['job_dict']['id'], 'status': 'complete'})
    print "\n SUCCESSULF JOB\N"
    print job_dict

    # Notify user of successful job
    send_notification(job_dict)


def add_failure(job=None, exc=None):
    """
    Subscriber that gets called when a job fails.
    """
    exception = traceback.format_exc()
    logging.error(exception)

    queue = Queue()
    job_dict = queue.update({
        'exc': exception,
        'status': 'failed',
        'id': job.kwargs['job_dict']['id']
    })

    # Notify user of failed job
    send_notification(job_dict, exception)
