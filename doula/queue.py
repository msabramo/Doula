import json
from retools.queue import QueueManager


def get_queue_name(job):
    queue_name_parts = job.queue_name.split(":")
    return queue_name_parts[0]


def pop_job(r, key, job_id):
    for j in r.smembers(key):
        j = json.loads(j)
        if r.id == job_id:
            r.srem(key, json.dumps(r))
            return r


def add_job(job=None):
    p = job.redis.pipeline()
    queue_name = get_queue_name(job)
    key = "doula:" + queue_name + ":jobs"

    value = {
        'id': job.job_id,
        'status': 'queued',
        'job_type': job.kwargs['_type'],
        'env': job.kwargs['env'],
        'service': job.kwargs['service']
    }

    p.sadd(key, json.dumps(value))


def add_status(status, job=None, result=None, exc=None):
    p = job.redis.pipeline()
    queue_name = get_queue_name(job)
    key = "doula:" + queue_name + ":jobs"

    job = pop_job(job.redis, key, job.job_id)
    job.status = status

    p.lpush(key, json.dumps(job))


def add_result(job=None, result=None):
    add_status('completed', job=job, result=None)


def add_failure(job=None, exc=None):
    add_status('failed', job=job, exc=None)


class Queue(object):

    def __init__(self):
        self.qm = QueueManager()
        self.qm.subscriber('job_prerun', handler='doula.queue:add_job')
        self.qm.subscriber('job_postrun', handler='doula.queue:add_result')
        self.qm.subscriber('job_failure', handler='doula.queue:add_failure')

    def this(self, _type, env, service, job, **kwargs):
        if _type and env and service:
            self.qm.enqueue(job,
                            _type=_type,
                            env=env,
                            service=service,
                            **kwargs)
        else:
            raise Exception

    def get(self, env, service):
        pass
