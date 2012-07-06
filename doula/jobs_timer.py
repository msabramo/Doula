"""
Schedule tasks to be put on the queue that need to be continually updated.
"""

from apscheduler.scheduler import Scheduler
from doula.config import Config
from doula.queue import Queue
import uuid


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


def start_task_scheduling():
	"""Start scheduling tasks."""
	sched = Scheduler()
	sched.start()
	# alextodo change seconds to minutes
	sched.add_interval_job(pull_cheeseprism_data, seconds=int(Config.get('task_interval')))