from retools.queue import QueueManager


def add_job(job=None):
    p = job.redis.pipeline()
    import pdb;pdb.set_trace()


def add_result(job=None, result=None):
    p = job.redis.pipeline()
    import pdb;pdb.set_trace()


def add_failure(job=None, exc=None):
    p = job.redis.pipeline()
    import pdb;pdb.set_trace()


class Queue(object):

    def __init__(self):
        self.qm = QueueManager()
        self.qm.subscriber('job_prerun', handler='doula.queue:add_job')
        self.qm.subscriber('job_postrun', handler='doula.queue:add_result')
        self.qm.subscriber('job_failure', handler='doula.queue:add_failure')

    def this(self, job, **kwargs):
        self.qm.enqueue(job, **kwargs)

    def get(self, env, service):
        pass
