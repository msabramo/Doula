import supervisor
from doula.models.package import Package


def push_to_cheeseprism(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'push_to_cheeseprism'
    """
    p = Package(job_dict['service'], job_dict['remote'])
    p.distribute(job_dict['branch'], job_dict['version'])


def cycle_services(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'
    """
    supervisor.restart()
