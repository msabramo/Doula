"""
Schedule tasks to be put on the queue that need to be continually updated.
"""

from apscheduler.scheduler import Scheduler
from doula.config import Config
from doula.queue import Queue
import uuid


def pull_github_data():
    """

    """
    job_dict = {
        'id': uuid.uuid1().hex,
        'job_type': 'pull_github_data'
    }

    q = Queue()
    q.this(job_dict)


def pull_cheeseprism_data():
    """
    Update the cached data. ex. CheesePrism Data, Git commit history.
    Put the tasks on the queue
    """
    job_dict = {
        'id': uuid.uuid1().hex,
        'job_type': 'pull_cheeseprism_data'
    }

    q = Queue()
    q.this(job_dict)


def pull_bambino_data():
    """
    Update the cached bambino data
    """
    job_dict = {
        'id': uuid.uuid1().hex,
        'job_type': 'pull_bambino_data'
    }

    q = Queue()
    q.this(job_dict)


def start_task_scheduling():
    """
    Start scheduling tasks.
    """
    sched = Scheduler()
    sched.start()
    # alextodo change seconds to minutes
    interval = int(Config.get('task_interval'))
    sched.add_interval_job(pull_bambino_data, seconds=interval)
    sched.add_interval_job(pull_github_data, seconds=interval)
    sched.add_interval_job(pull_cheeseprism_data, seconds=interval)
