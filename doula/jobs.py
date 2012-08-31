from datetime import datetime
from doula.cache import Cache
from doula.config import Config
from doula.github.github import pull_appenv_repos
from doula.github.github import pull_devmonkeys_repos
from doula.models.node import Node
from doula.models.package import Package
from doula.models.push import Push
from doula.models.service import Service
from doula.models.sites_dal import SiteDAL
from doula.queue import Queue
from doula.services.cheese_prism import CheesePrism
from doula.util import *
import logging
import os
import time
import traceback
import xmlrpclib

class ContextFilter(logging.Filter):
    """
    This is a filter which removes the shit

    """

    def filter(self, record):
        print record.getMessage()

        if "Secsh channel" in record.getMessage():
            return False
        return True


def create_logger(job_id, level=logging.DEBUG):
    logging.basicConfig(filename=os.path.join('/var/log/doula', str(job_id) + '.log'),
                        format='%(asctime)s %(levelname)-4s %(message)s',
                        level=level)
    return logging.getLogger()


def load_config(config):
    """
    Load the config as a global
    """
    Config.load_config(config)


def push_to_cheeseprism(config={}, job_dict={}):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'push_to_cheeseprism'.  Upon being called, it will
    updated the version present in the setup.py of the repo, and release the
    package to cheeseprism.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info("About to push package to cheese prism %s" % job_dict['remote'])

        p = Package(job_dict['service'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

        logging.info('Finished pushing package %s to CheesePrism' % job_dict['remote'])
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def cycle_services(config={}, job_dict={}):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'.  Upon being called, it will restart
    the necessary supervisor processes to make the changes to the packages live
    on a specific site.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('Cycling service %s' % job_dict['service'])

        for ip in job_dict['nodes']:
            logging.info('Cycling supervisord services: %s' % job_dict['supervisor_service_names'])

            for name in job_dict['supervisor_service_names']:
                logging.info('Cycling service %s on IP http://%s' % (name, ip))
                Service.cycle(xmlrpclib.ServerProxy('http://' + ip), name)

        logging.info('Done cycling %s' % job_dict['service'])
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_cheeseprism_data(config={}, job_dict={}):
    """
    Ping Cheese Prism and pull the latest packages and all of their versions.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('Started pulling cheeseprism data')

        cache = Cache.cache()
        pipeline = cache.pipeline()

        packages = CheesePrism.pull_all_packages()
        pipeline.set("cheeseprism:packages", dumps(packages))

        for pckg in packages:
            pipeline.set('cheeseprism:package:' + pckg.clean_name, dumps(pckg))

        pipeline.execute()

        logging.info('Done pulling data from cheeseprism')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_github_data(config={}, job_dict={}):
    """
    Pull the github data for every python package.
    Pull commit history, tags, branches. Everything.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('pulling github data')

        repos = pull_devmonkeys_repos()
        cache = Cache.cache()
        cache.set("repos:devmonkeys", dumps(repos))

        logging.info('Done pulling github data')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_appenv_github_data(config={}, job_dict={}, debug=False):
    """
    Pull the github data for every App environment
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('Pulling github appenv data')

        cache = Cache.cache()
        repos = pull_appenv_repos()
        cache.set("repos:appenvs", dumps(repos))

        logging.info('Done pulling github appenv data')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def push_service_environment(config={}, job_dict={}, debug=False):
    """
    Pip install the packages sent
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        #TODO: verbose statemenet
        f = ContextFilter()
        log.addFilter(f)
        log.info('%s pushed the following packages to %s: [%s]' %
                (job_dict['user_id'], job_dict['service_name'], ','.join(job_dict['packages'])))
        failures = []
        successes = []

        try:
            push = Push(
                job_dict['service_name'],
                job_dict['user_id'],
                config['bambino.webapp_dir'],
                config['doula.cheeseprism_url'],
                config['doula.keyfile_path'],
                job_dict['site_name_or_node_ip'],
                debug
            )
            successes, failures = push.packages(job_dict['packages'])
        except Exception as e:
            print 'EXCEPTIN IN JOB:'
            # getting this message. sequence item 0: exp
            print e.message
            failures.append({'package': 'git', 'error': str(e)})

        if failures:
            # timtodo. this used to use join, failures returns this
            # [{'error': "'bambino.web_app_dir'", 'package': 'git'}]
            # Old call. this is here
            # raise Exception(','.join(failures['error']))
            raise Exception(failures[0]['error'])

        logging.getLogger().setLevel(logging.DEBUG)
        create_logger(job_dict['id'])
        logging.info('Done installing packages.')
        return successes, failures
    except Exception as e:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def pull_bambino_data(config={}, job_dict={}):
    """
    Pull the data from all the bambino's
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('Pulling bambino data')

        cache = Cache.cache()
        pipeline = cache.pipeline()
        simple_sites = SiteDAL.get_simple_sites()

        for site_name in simple_sites:
            simple_site = simple_sites[site_name]
            simple_nodes = simple_site['nodes']

            for name, n in simple_nodes.iteritems():
                node = Node(name, n['site'], n['url'])
                services_as_json = node.pull_services()
                pipeline.set('node:services:' + node.name_url, services_as_json)

        pipeline.execute()
        logging.info('Done pulling bambino data')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def cleanup_queue(config={}, job_dict={}):
    """
    Cleanup old jobs stored in our queueing system.
    """
    create_logger(job_dict['id'])
    load_config(config)

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
