from doula.cache import Cache
from doula.github.github import pull_devmonkeys_repos
from doula.models.node import Node
from doula.models.package import Package
from doula.models.service import Service
from doula.models.sites_dal import SiteDAL
from doula.services.cheese_prism import CheesePrism
from doula.util import *
from doula.config import Config
from doula.queue import Queue
from datetime import datetime
import os
import json
import logging
import sys
import traceback
import xmlrpclib
import time


def create_logger(job_id):
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    fh = logging.FileHandler(os.path.join('/var/log/doula', str(job_id) + '.log'))
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)

    return log


def load_config():
    """
    Load the config from redis
    """
    cache = Cache.cache()
    settings_as_json = cache.get('doula_settings')
    Config.load_config(json.loads(settings_as_json))


def push_to_cheeseprism(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'push_to_cheeseprism'.  Upon being called, it will
    updated the version present in the setup.py of the repo, and release the
    package to cheeseprism.
    """
    log = create_logger(job_dict['id'])
    try:
        log.info("About to push package to cheese prism %s" % job_dict['remote'])
        load_config()

        p = Package(job_dict['service'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

        log.info('Finished pushing package %s to CheesePrism' % job_dict['remote'])
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def cycle_services(job_dict):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'.  Upon being called, it will restart
    the necessary supervisor processes to make the changes to the packages live
    on a specific site.
    """
    log = create_logger(job_dict['id'])
    load_config()
    try:
        for ip in job_dict['nodes']:
            for name in job_dict['supervisor_service_names']:
                log.info('Cycling service %s on IP http://%s' % (name, ip))
                Service.cycle(xmlrpclib.ServerProxy('http://' + ip), name)

        log.info('Done cycling services')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_cheeseprism_data(job_dict=None):
    """
    Ping Cheese Prism and pull the latest packages and all of their versions.
    """
    log = create_logger(job_dict['id'])
    try:
        log.info('Started pulling cheeseprism data')
        load_config()

        cache = Cache.cache()
        pipeline = cache.pipeline()

        packages = CheesePrism.pull_all_packages()
        pipeline.set("cheeseprism_packages", dumps(packages))

        for pckg in packages:
            pckg.pull_versions()
            pipeline.set('cheeseprism_pckg_' + pckg.clean_name, dumps(pckg))

        pipeline.execute()

        log.info('Done pulling data from cheeseprism')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_github_data(job_dict=None):
    """
    Pull the github data for every python package.
    Pull commit history, tags, branches. Everything.
    """
    log = create_logger(job_dict['id'])
    try:
        log.info('pulling github data')
        load_config()
        repos = pull_devmonkeys_repos()
        cache = Cache.cache()
        cache.set("devmonkeys_repos", dumps(repos))

        log.info('Done pulling github data')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_bambino_data(job_dict=None):
    """
    Pull the data from all the bambino's
    """
    log = create_logger(job_dict['id'])
    try:
        log.info('Pulling bambino data')
        load_config()

        cache = Cache.cache()
        pipeline = cache.pipeline()
        simple_sites = SiteDAL.get_simple_sites()

        for site_name in simple_sites:
            simple_site = simple_sites[site_name]
            simple_nodes = simple_site['nodes']

            for name, n in simple_nodes.iteritems():
                node = Node(name, n['site'], n['url'])
                services_as_json = node.pull_services()
                pipeline.set('node_services_' + node.name_url, services_as_json)

        pipeline.execute()
        log.info('Done pulling bambino data')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def cleanup_queue(job_dict=None):
    """
    Cleanup unneeded jobs stored in our queueing system.
    """
    log = create_logger(job_dict['id'])
    try:
        log.info('Cleaning up the queue')

        now = datetime.now()
        now = time.mktime(now.timetuple())

        queue = Queue()
        jobs = queue.get()
        # Get completed jobs that need to be deleted
        complete_job_ids = [job['id'] for job in jobs if job['time_started'] < now - 7200 and job['status'] == 'complete']
        # Get failed jobs that need to be deleted
        failed_job_ids = [job['id'] for job in jobs if job['time_started'] < now - 14400 and job['status'] == 'failed']

        ids = complete_job_ids + failed_job_ids
        # Remove completed jobs and failed jobs that are unneeded
        queue.remove(ids)
        # Remove all completed and failed logs
        for id in ids:
            os.remove(os.path.join('/var/log/doula', id + '.log'))

        log.info('Done cleaning up the queue')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise
