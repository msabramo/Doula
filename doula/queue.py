from doula.cache import Cache
from doula.notifications import send_notification
from retools.queue import QueueManager
import simplejson as json
import logging
import time
import traceback
import uuid
import math


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
        'email': '',
        'service_name': '',
        'assets_outdir': '',
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
        'push_service_environment': push_service_environment_dict,
        'cycle_services': common_dict,
        'pull_cheeseprism_data': common_dict,
        'pull_github_data': common_dict,
        'pull_appenv_github_data': common_dict,
        'pull_bambino_data': common_dict,
        'cleanup_queue': common_dict
    }

    def __init__(self):
        # Initialize redis database
        self.redis = Cache.cache()

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
            'push_service_environment',
            'cycle_services',
            'pull_cheeseprism_data',
            'pull_github_data',
            'pull_appenv_github_data',
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

        p = self.redis.pipeline()

        self.qm.enqueue('doula.jobs:%s' % job_type, config=self.get_config(), job_dict=job_dict)
        self._save(p, job_dict)
        p.execute()

        # Anytime a job is added we update the buckets
        self.update_buckets()

        return job_dict['id']

    def get_config(self):
        """
        Load the config from redis
        """
        return json.loads(self.redis.get('doula:settings'))

    def update(self, job_dict):
        if not 'id' in job_dict:
            raise Exception('Must pass an id into the update function.')

        p = self.redis.pipeline()
        job_dict = self._update(p, job_dict)
        p.execute()

        return job_dict

    def remove(self, job_dict_ids):
        if isinstance(job_dict_ids, basestring):
            job_dict_ids = [job_dict_ids]

        p = self.redis.pipeline()
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
        jobs_json = self.redis.smembers(k['jobs'])

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

    #######################
    # Query Section of Queue
    #######################

    # alextodo. put together tests for this ish. make it work.
    # publish by 10 am.

    def has_bucket_changed(self, bucket_id, last_updated_for_bucket):
        last_updated = self.redis.get('doula.query.bucket.last_updated:' + bucket_id)
        self.extend_bucket_expiration(bucket_id)

        if not last_updated:
            last_updated = 1

        last_updated = int(math.floor(float(last_updated)))
        last_updated_for_bucket = int(math.floor(float(last_updated_for_bucket)))

        if int(math.floor(last_updated_for_bucket)) < int(math.floor(last_updated)):
            return True
        else:
            return False

    def extend_bucket_expiration(self, bucket_id):
        """
        Every query extends the life of the bucket for 5 minutes
        """
        self.redis.expire('doula.query.bucket:' + bucket_id, 30)
        self.redis.expire('doula.query.bucket.last_updated:' + bucket_id, 30)

    def get_query_bucket(self, bucket_id, query):
        """
        Check if a bucket exist under the ID, if so return it,
        otherwise build and return the new query bucket
        """
        bucket = None

        if bucket_id:
            bucket_as_json = self.redis.get('doula.query.bucket:' + bucket_id)

            if bucket_as_json:
                bucket = json.loads(bucket_as_json)

        if not bucket:
            # build a bucket and save it
            bucket = {
                "id": uuid.uuid1().hex,
                "query": query,
                "last_updated": time.time(),
                "jobs": self.get(query)
            }

            self.save_bucket_cache_values(bucket)

        return bucket

    def save_bucket_cache_values(self, bucket):
        """
        Add the bucket to the list of buckets and save it's last_updated time
        and save the bucket as json
        """
        self.redis.sadd('doula.query.buckets', bucket['id'])
        self.redis.set('doula.query.bucket:' + bucket['id'], json.dumps(bucket))
        self.redis.set('doula.query.bucket.last_updated:' + bucket['id'], bucket['last_updated'])

        self.extend_bucket_expiration(bucket['id'])

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

    def update_buckets(self):
        """
        Update all the buckets in the 'doula.query.buckets' set with newest details
        """
        for bucket_id in self.redis.smembers('doula.query.buckets'):
            bucket_as_json = self.redis.get('doula.query.bucket:' + bucket_id)

            if bucket_as_json:
                bucket = json.loads(bucket_as_json)
                bucket["last_updated"] = time.time()
                bucket["jobs"] = self.get(bucket["query"])
                self.save_bucket_cache_values(bucket)
            else:
                # bucket expired. remove from doula.query.buckets set
                self.redis.srem("doula.query.buckets", bucket_id)


#
# Retools Subscribers
#
def add_result(job=None, result=None):
    """
    Subscriber that gets called right after the job gets run, and is successful.
    """
    print "\n SUCCESSFUL JOB\N"
    print job.kwargs['job_dict']

    if can_update_job(job.kwargs['job_dict']['job_type']):
        queue = Queue()

        job_dict = queue.update({'id': job.kwargs['job_dict']['id'], 'status': 'complete'})

        # Update the buckets with the newest details
        queue.update_buckets()

        # Notify user of successful job
        send_notification(job_dict)


def add_failure(job=None, exc=None):
    """
    Subscriber that gets called when a job fails.
    """
    tb = traceback.format_exc()
    logging.error(exc)

    print "\n FAILED JOB"
    print exc
    print tb

    if can_update_job(job.kwargs['job_dict']['job_type']):
        queue = Queue()
        job_dict = queue.update({
            'exc': tb,
            'status': 'failed',
            'id': job.kwargs['job_dict']['id']
        })

        queue.update_buckets()

        # Notify user of failed job
        send_notification(job_dict, tb)


def can_update_job(job_type):
    """
    Determines if the job can be updated by according to its type
    We never have to update the maintenance_job_types
    """
    updateable_job_types = [
        'push_to_cheeseprism',
        'cycle_services',
        'push_service_environment'
        ]

    return job_type in updateable_job_types
