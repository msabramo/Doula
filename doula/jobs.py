from doula.cache import Cache
from doula.models.sites import Package
from doula.services.cheese_prism import CheesePrism
from doula.util import *
import json
import supervisor
import traceback

cache = Cache.cache()

def push_to_cheeseprism(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'push_to_cheeseprism'
    joetodo be descriptive about what the task actually does.
    """
    # joetodo, get the version number too
    p = Package(job_dict['service'], '0')
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
    # alexgtodo, update the log file
    try:
        pipeline = cache.pipeline()

        packages = CheesePrism.pull_all_packages()
        pipeline.set("cheeseprism_packages", dumps(packages))

        for pckg in packages:
            pckg.pull_versions()
            pipeline.set('cheeseprism_pckg_' + pckg.clean_name, dumps(pckg))

        pipeline.execute()

        print 'done pulling data from cheeseprism'
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
    pass