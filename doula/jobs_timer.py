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
    _queue_up('pull_github_data')


def pull_releases_for_all_services():
    _queue_up('pull_releases_for_all_services')


def pull_service_configs():
    _queue_up('pull_service_configs')


def pull_cheeseprism_data():
    """
    Update the redisd data. ex. CheesePrism Data, Git commit history.
    Put the tasks on the queue
    """
    _queue_up('pull_cheeseprism_data')


def pull_bambino_data():
    """
    Update the redisd bambino data
    """
    _queue_up('pull_bambino_data')


def cleanup_queue():
    """
    Update the redisd bambino data
    """
    _queue_up('cleanup_queue')


def add_webhook_callbacks():
    """
    Add the webhook callbacks
    """
    _queue_up('add_webhook_callbacks')


def _queue_up(name):
    q = Queue()
    q.enqueue({'job_type': name})


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

    interval = int(Config.get('task_interval_pull_releases_for_all_services'))
    sched.add_interval_job(pull_releases_for_all_services, seconds=interval)

    interval = int(Config.get('tast_interval_pull_service_configs'))
    sched.add_interval_job(pull_service_configs, seconds=interval)

    cleanup_interval = int(Config.get('task_interval_cleanup_queue'))
    sched.add_interval_job(cleanup_queue, seconds=cleanup_interval)

    interval = int(Config.get('tast_interval_add_webhook_callbacks'))
    sched.add_interval_job(add_webhook_callbacks, seconds=interval)
