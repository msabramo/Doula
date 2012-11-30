"""
Schedule tasks to be put on the queue that need to be continually updated.
"""

from apscheduler.scheduler import Scheduler
from doula.config import Config
from doula.queue import Queue


def pull_github_data():
    """
    Pull the data for the dev monkeys org
    """
    job_dict = {
        'job_type': 'pull_github_data'
    }

    q = Queue()
    q.this(job_dict)


def pull_appenv_github_data():
    job_dict = {
        'job_type': 'pull_appenv_github_data'
    }

    q = Queue()
    q.this(job_dict)


def pull_cheeseprism_data():
    """
    Update the redisd data. ex. CheesePrism Data, Git commit history.
    Put the tasks on the queue
    """
    job_dict = {
        'job_type': 'pull_cheeseprism_data'
    }

    q = Queue()
    q.this(job_dict)


def pull_bambino_data():
    """
    Update the redisd bambino data
    """
    job_dict = {
        'job_type': 'pull_bambino_data'
    }

    q = Queue()
    q.this(job_dict)


def cleanup_queue():
    """
    Update the redisd bambino data
    """
    job_dict = {
        'job_type': 'cleanup_queue'
    }

    q = Queue()
    q.this(job_dict)


def start_task_scheduling():
    """
    Start scheduling tasks.
    """
    sched = Scheduler()
    sched.start()

    interval = int(Config.get('task_interval_pull_bambino'))
    sched.add_interval_job(pull_bambino_data, seconds=interval)

    cheeseprism_interval = int(Config.get('task_interval_pull_cheesprism_data'))
    sched.add_interval_job(pull_cheeseprism_data, seconds=cheeseprism_interval)

    git_interval = int(Config.get('task_interval_pull_github_data'))
    sched.add_interval_job(pull_github_data, seconds=git_interval)

    interval = int(Config.get('task_interval_pull_appenv_github_data'))
    sched.add_interval_job(pull_appenv_github_data, seconds=interval)

    cleanup_interval = int(Config.get('task_interval_cleanup_queue'))
    sched.add_interval_job(cleanup_queue, seconds=cleanup_interval)
