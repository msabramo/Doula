import json
from retools.queue import QueueManager


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
        self.qm = QueueManager()
        self.qm.subscriber('job_postrun', handler='doula.queue:add_result')
        self.qm.subscriber('job_failure', handler='doula.queue:add_failure')

    def this(self, job_dict):
        self.qm.enqueue('doula.jobs:push_to_cheeseprism', job_dict=job_dict)

    def get(self, job_dict):
        pass


def keys(job=None):
    """
    Returns the standard keys for interacting with redis.
    """
    queue_name_parts = job.queue_name.split(":")
    queue_name = queue_name_parts[0]

    return {
        'jobs': 'doula:jobs:' + queue_name
    }


def attrs(job, attrs):
    """
    Given a job and the attributes to change on it, saves our "Job" dict
    """
    k = keys(job)
    p = job.redis.pipeline()

    job_dict = job.kwargs['job_dict']
    for k, v in attrs:
        job_dict[k] = v

    p.sadd(k['jobs'], json.dumps(job_dict))
    p.execute()


def add_result(job=None, result=None):
    """
    Subscriber that gets called right after the job gets run, and is successful.
    """
    attrs(job, {'status': 'complete'})


def add_failure(job=None, exc=None):
    """
    Subscriber that gets called when a job fails.
    """
    attrs(job, {'status': 'failed'})
