from doula.cache import Cache
from doula.github.github import pull_devmonkeys_repos
from doula.models.node import Node
from doula.models.package import Package
from doula.models.service import Service
from doula.models.sites_dal import SiteDAL
from doula.models.push import Push
from doula.services.cheese_prism import CheesePrism
from doula.util import *
from doula.config import Config
from doula.queue import Queue
from datetime import datetime
import os
import json
import logging
import traceback
import xmlrpclib
import time


def create_logger(job_id):
    logging.basicConfig(filename=os.path.join('/var/log/doula', str(job_id) + '.log'), level=logging.DEBUG)


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
    create_logger(job_dict['id'])
    try:
        logging.info("About to push package to cheese prism %s" % job_dict['remote'])
        load_config()

        p = Package(job_dict['service'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

        logging.info('Finished pushing package %s to CheesePrism' % job_dict['remote'])
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def cycle_services(job_dict):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'.  Upon being called, it will restart
    the necessary supervisor processes to make the changes to the packages live
    on a specific site.
    """
    create_logger(job_dict['id'])
    load_config()

    try:
        log.info('Cycling service %s' % job_dict['name'])

        for ip in job_dict['nodes']:
            for name in job_dict['supervisor_service_names']:
                logging.info('Cycling service %s on IP http://%s' % (name, ip))
                Service.cycle(xmlrpclib.ServerProxy('http://' + ip), name)

        logging.info('Done cycling %s' % job_dict['name'])
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_cheeseprism_data(job_dict=None):
    """
    Ping Cheese Prism and pull the latest packages and all of their versions.
    """
    create_logger(job_dict['id'])
    try:
        logging.info('Started pulling cheeseprism data')
        load_config()

        cache = Cache.cache()
        pipeline = cache.pipeline()

        packages = CheesePrism.pull_all_packages()
        pipeline.set("cheeseprism_packages", dumps(packages))

        for pckg in packages:
            pckg.pull_versions()
            pipeline.set('cheeseprism_pckg_' + pckg.clean_name, dumps(pckg))

        pipeline.execute()

        logging.info('Done pulling data from cheeseprism')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_github_data(job_dict=None):
    """
    Pull the github data for every python package.
    Pull commit history, tags, branches. Everything.
    """
    create_logger(job_dict['id'])
    try:
        logging.info('pulling github data')
        load_config()
        repos = pull_devmonkeys_repos()
        cache = Cache.cache()
        cache.set("devmonkeys_repos", dumps(repos))

        logging.info('Done pulling github data')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def push_service_environment(job_dict=None):
    """
    Pip install the packages sent
    """
    create_logger(job_dict['id'])
    try:
        #TODO: verbose statemenet
        logging.info('pushing code to environment')
        load_config()
        failures = []

        try:
            push = Push(
                Config.get('bambino.web_app_dir'),
                Config.get('doula.cheeseprism_url'),
                Config.get('doula.keyfile_path'),
                job_dict['node_name_or_ip']
            )
            successes, failures = push.packages(job_dict['service_name'])
            push.config(job_dict['service_name'])
        except Exception as e:
            failures.append({'package': 'git', 'error': str(e)})

        if failures:
            raise Exception(json.dumps(failures))

        logging.info('Done installing packages.')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_bambino_data(job_dict=None):
    """
    Pull the data from all the bambino's
    """
    create_logger(job_dict['id'])
    try:
        logging.info('Pulling bambino data')
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
        logging.info('Done pulling bambino data')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def cleanup_queue(job_dict=None):
    """
    Cleanup unneeded jobs stored in our queueing system.
    """
    create_logger(job_dict['id'])
    try:
        logging.info('Cleaning up the queue')

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

        logging.info('Done cleaning up the queue')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise
