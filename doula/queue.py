from doula.cache import Redis
from doula.notifications import send_notification
from retools.queue import QueueManager
from doula.cache_keys import key_val
import simplejson as json
import logging
import time
import traceback
import uuid
import math


class Queue(object):
    """
    The Queue class handles enqueuing jobs added to the Doula queue. It allows
    the rest of the application to query and update the queue.
    """
    default_queue_name = 'main'
    maintenance_queue_name = 'maintenance'

    base_job_dict = {
        'id': 0,
        'user_id': '',
        'status': '',
        'job_type': '',
        'site': '',
        'service': '',
        'time_started': 0,
        'exc': ''
    }

    standard_job_types = {
        'build_new_package',
        'release_service',
        'cycle_service'
    }

    maintenance_job_types = [
        'add_webhook_callbacks',
        'pull_releases_for_all_services',
        'pull_service_configs',
        'pull_service_configs_for_service',
        'pull_cheeseprism_data',
        'pull_github_data',
        'cleanup_queue']

    def __init__(self):
        # Initialize redis database
        self.redis = Redis.get_instance()

        # Initialize the QueueManager
        self.qm = QueueManager(default_queue_name=self.default_queue_name)
        self.maint_qm = QueueManager(default_queue_name=self.maintenance_queue_name)
        self.qm.subscriber('job_postrun', handler='doula.queue:add_result')
        self.qm.subscriber('job_failure', handler='doula.queue:add_failure')

    def enqueue(self, new_job_dict):
        """
        Enqueues a job onto the retools queue
        """
        job_dict = self.build_valid_job_dict(new_job_dict)
        queue_name = 'doula.jobs:%s' % job_dict['job_type']

        if self.is_maintenance_job(job_dict['job_type']):
            self.maint_qm.enqueue(queue_name, config=self.get_config(), job_dict=job_dict)
        else:
            self.qm.enqueue(queue_name, config=self.get_config(), job_dict=job_dict)

        self.save_job(job_dict)

        # Anytime a job is added we update the buckets
        self.update_buckets()

        return job_dict['id']

    def build_valid_job_dict(self, new_job_dict):
        """Build a job dict with all required keys"""
        job_dict = self.base_job_dict.copy()
        job_dict.update(new_job_dict)

        # Generate new UUID used to identify the job
        job_dict['id'] = uuid.uuid1().hex
        job_dict['status'] = 'queued'
        job_dict['time_started'] = time.time()

        return job_dict

    def is_maintenance_job(self, job_type):
        """Determine if job_type is maintenance job"""
        return job_type in self.maintenance_job_types

    def is_standard_job(self, job_type):
        """Determine if the job_type is a standard job"""
        return job_type in self.standard_job_types

    def get_config(self):
        """Load the config from redis"""
        return json.loads(self.redis.get('doula:settings'))

    def save_job(self, new_job_dict):
        """Save or update the job_dict"""
        job_dict_as_json = self.redis.hget(self._job_queue_key(), new_job_dict['id'])

        if job_dict_as_json:
            # update existing
            job_dict = json.loads(job_dict_as_json)
            job_dict.update(new_job_dict)
        else:
            # save new job
            job_dict = new_job_dict

        job_dict_as_json = json.dumps(job_dict, sort_keys=True)

        self.redis.hset(self._job_queue_key(), job_dict['id'], job_dict_as_json)

        return job_dict

    def remove(self, job_ids):
        """Remove the job ids."""
        if isinstance(job_ids, basestring):
            job_ids = [job_ids]

        for id in job_ids:
            self.redis.hdel(self._job_queue_key(), id)

    def _job_queue_key(self):
        """Return retools job queue key"""
        return key_val("job_queue", {"queue": self.default_queue_name})

    def _all_jobs(self):
        """Return all the jobs on the queue"""
        return self.redis.hgetall(self._job_queue_key())

    def find_jobs(self, original_job_dict_query={}):
        """
        Find the jobs that meet criteria sent in the job_dict
        """
        found_jobs = []
        job_dict_query = original_job_dict_query.copy()
        find_these_job_types = None

        if 'job_type' in job_dict_query:
            find_these_job_types = job_dict_query['job_type']
            del job_dict_query['job_type']

        job_dict_query_set = set(job_dict_query.items())

        # http://docs.python.org/2/library/stdtypes.html#set.intersection
        for id, job_as_json in self._all_jobs().iteritems():
            job_dict = json.loads(job_as_json)

            # If no job_type key in job_dict. move on
            if not 'job_type' in job_dict:
                continue

            # If job is NOT a standard job, skip it
            if not self.is_standard_job(job_dict.get('job_type', '')):
                continue

            # If find_these_job_types exists, skip if job_type not in list
            if find_these_job_types:
                if not job_dict['job_type'] in find_these_job_types:
                    continue

            if self.safe_job_dict_set(job_dict) >= job_dict_query_set:
                # Test whether every element in job_dict_query_set is in the job_dict
                found_jobs.append(job_dict)

        return found_jobs

    def safe_job_dict_set(self, job_dict):
        # Remove keys that will mess up the set() call.
        if 'exc' in job_dict:
            del job_dict['exc']

        if 'manifest' in job_dict:
            del job_dict['manifest']

        return set(job_dict.items())

    #######################
    # Query Section of Queue
    #######################

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

    def get_query_bucket(self, bucket_id, job_dict_query):
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
                "query": job_dict_query,
                "last_updated": time.time(),
                "jobs": self.find_jobs(job_dict_query)
            }

            bucket['query'] = job_dict_query

            self.save_bucket_redis_values(bucket)

        return bucket

    def update_buckets(self):
        """
        Update all the buckets in the 'doula.query.buckets' set with newest details
        """
        for bucket_id in self.redis.smembers('doula.query.buckets'):
            bucket_as_json = self.redis.get('doula.query.bucket:' + bucket_id)

            if bucket_as_json:
                bucket = json.loads(bucket_as_json)
                bucket["last_updated"] = time.time()
                bucket["jobs"] = self.find_jobs(bucket["query"])
                self.save_bucket_redis_values(bucket)
            else:
                # bucket expired. remove from doula.query.buckets set
                self.redis.srem("doula.query.buckets", bucket_id)

    def save_bucket_redis_values(self, bucket):
        """
        Add the bucket to the list of buckets and save it's last_updated time
        and save the bucket as json
        """
        self.redis.sadd('doula.query.buckets', bucket['id'])
        self.redis.set('doula.query.bucket:' + bucket['id'], json.dumps(bucket))
        self.redis.set('doula.query.bucket.last_updated:' + bucket['id'], bucket['last_updated'])

        self.extend_bucket_expiration(bucket['id'])


#############################
# Retools Event Subscribers
#############################

def update_job_after_completion(job_dict, status, tb=None):
    q = Queue()

    if q.is_standard_job(job_dict['job_type']):
        job_dict = q.save_job({
            'id': job_dict['id'],
            'status': status,
            'exc': tb
            })

        q.update_buckets()
        send_notification(job_dict, tb)
    else:
        # The job should just be removed
        q.remove(job_dict['id'])


def add_result(job=None, result=None):
    """
    Subscriber that gets called right after the job gets run, and is successful.
    """
    print "\n SUCCESSFUL JOB\N"
    print job.kwargs['job_dict']

    update_job_after_completion(job.kwargs['job_dict'], 'complete')


def add_failure(job=None, exc=None):
    """
    Subscriber that gets called when a job fails.
    """
    tb = traceback.format_exc()

    print "\n Job Failed"
    print tb

    update_job_after_completion(job.kwargs['job_dict'], 'failed', tb)