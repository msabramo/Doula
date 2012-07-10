from doula.cache import Cache
from doula.github.github import pull_devmonkeys_repos
from doula.models.package import Package
from doula.services.cheese_prism import CheesePrism
from doula.util import *
import logging
import supervisor
import traceback

log = logging.getLogger(__name__)
fh = logging.FileHandler('/var/log/doula/jobs.log')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(fh)
log.addHandler(ch)

cache = Cache.cache()


def push_to_cheeseprism(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'push_to_cheeseprism'
    joetodo be descriptive about what the task actually does.
    """
    p = Package(job_dict['service'], '0', job_dict['remote'])
    p.distribute(job_dict['branch'], job_dict['version'])


# joenote why pass in None? you must have a job_dict
def cycle_services(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'
    joetodo be descriptive about what the task actually does.
    """
    supervisor.restart()


def pull_cheeseprism_data(job_dict):
    """
    Ping Cheese Prism and pull the latest packages and all of their versions.
    """
    # alexgtodo, update the log file, use the correct log file
    try:
        pipeline = cache.pipeline()

        packages = CheesePrism.pull_all_packages()
        pipeline.set("cheeseprism_packages", dumps(packages))

        for pckg in packages:
            pckg.pull_versions()
            pipeline.set('cheeseprism_pckg_' + pckg.clean_name, dumps(pckg))

        pipeline.execute()

        log.info('Done pulling data from cheeseprism')
    except Exception as e:
        # alextodo, need to pass come up with a commone way to handle failure
        print e
        print traceback.format_exc()
        raise


def pull_github_data(job_dict):
    """
    Pull the github data for every python package.
    Pull commit history, tags, branches. Everything.
    """
    try:
        repos = pull_devmonkeys_repos()
        cache.set("devmonkeys_repos", dumps(repos))

        print 'Done pulling github data'
    except Exception as e:
        print e
        print traceback.format_exc()
        raise
