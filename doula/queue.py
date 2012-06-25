import json
import redis
from retools.queue import QueueManager

default_queue_name = 'main'

common_dict = {
    'id': 0,
    'status': '',
    'job_type': '',
    'site': '',
    'service': '',
    'time_started': 0,
    'log_file': ''
}

push_to_cheeseprism_dict = dict({
    'remote': '',
    'branch': '',
    'version': ''
}.items() + common_dict.items())
cycle_services_dict = dict({}.items() + common_dict.items())

base_dicts = {
    'push_to_cheeseprism': push_to_cheeseprism_dict,
    'cycle_services': cycle_services_dict
}

# Initialize redis database
rdb = redis.Redis()


def keys():
    """
    Returns the standard keys for interacting with redis.
    """
    return {
        'jobs': 'doula:jobs:' + default_queue_name
    }


def get_jobs(queue_name):
    # Combine the two job locations
    jobs_json = rdb.smembers('doula:jobs:' + queue_name)

    # Created a list of all of the jobs(dict)
    jobs = []
    for job_json in jobs_json:
        job = json.loads(job_json)
        jobs.append(job)

    return jobs


def get_job(queue_name, id):
    jobs = get_jobs(queue_name)

    for job in jobs:
        if job['id'] == id:
            return job


def pop_job(queue_name, id):
    jobs = get_jobs(queue_name)
    p = rdb.pipeline()

    for job in jobs:
        if job['id'] == id:
            p.srem(queue_name, json.dumps(job))
            p.execute()
            return job


def save(attrs):
    """
    Given a complete or partial "Job" dict, saves it
    """
    k = keys()
    p = rdb.pipeline()

    _type = attrs['job_type']
    job_dict = base_dicts[_type]
    for key, val in attrs.items():
        job_dict[key] = val

    p.sadd(k['jobs'], json.dumps(job_dict))
    p.execute()


def update(attrs):
    """
    Updates a specific "Job" dict, must be give an id
    """
    k = keys()
    p = rdb.pipeline()

    job_dict = pop_job(default_queue_name, attrs['id'])
    for key, val in attrs.items():
        job_dict[key] = val

    p.sadd(k['jobs'], json.dumps(job_dict))
    p.execute()


class Queue(object):
    """
    This class represents all of Doula's interaction with the queueing
    engine.  The common link between Doula and this class is the
    "Job" dict.  This "Job" dict is of the following format:

    Common for every job:
    {
        id: "",
        status: (queued, completed, failed),
        job_type: (push_package|cycle_service)
        site: '',
        service: '',
        time_started: '',
        log_file: 'path to log file to write to'
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

    def __init__(self):
        self.qm = QueueManager(default_queue_name=default_queue_name)
        self.qm.subscriber('job_postrun', handler='doula.queue:add_result')
        self.qm.subscriber('job_failure', handler='doula.queue:add_failure')

    def this(self, job_dict):
        id = None
        job_type = job_dict['job_type']

        if job_type is 'push_to_cheeseprism':
            id = self.qm.enqueue('doula.jobs:push_to_cheeseprism')
        elif job_type is 'cycle_services':
            id = self.qm.enqueue('doula.jobs:cycle_services')

        job_dict['id'] = id
        save(job_dict)
        return id

    def get(self, job_dict):
        jobs = get_jobs(default_queue_name)

        # Loop through each criteria, throw out the jobs that don't meet
        for job in jobs:
            for k, v in job_dict.items():
                try:
                    if job[k] != v:
                        jobs.remove(job)
                except KeyError:
                    continue

        return jobs


#
# Retools Subscribers
#
def add_result(job=None, result=None):
    """
    Subscriber that gets called right after the job gets run, and is successful.
    """
    update({'id': job.job_id, 'status': 'complete'})


def add_failure(job=None, exc=None):
    """
    Subscriber that gets called when a job fails.
    """
    update({'id': job.job_id, 'status': 'failed'})
