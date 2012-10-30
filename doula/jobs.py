from doula.cache import Cache
from doula.cheese_prism import CheesePrism
from doula.config import Config
from doula.github import pull_appenv_repos
from doula.github import pull_devmonkeys_repos
from doula.models.node import Node
from doula.models.package import Package
from doula.models.push import Push
from doula.models.service import Service
from doula.models.sites_dal import SiteDAL
from doula.queue import Queue
from doula.util import *
import logging
import os
import simplejson as json
import time
import traceback
import uuid
import xmlrpclib
import socket


def create_logger(job_id, level=logging.INFO):
    logging.basicConfig(filename=os.path.join('/var/log/doula', str(job_id) + '.log'),
                        format='%(asctime)s %(levelname)-4s %(message)s',
                        level=level)
    return logging.getLogger()


def load_config(config):
    """
    Load the config as a global
    """
    Config.load_config(config)


def build_new_package(config={}, job_dict={}):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'build_new_package'.  Upon being called, it will
    updated the version present in the setup.py of the repo, and release the
    package to cheeseprism.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        # alextodo. revisit everything we log to the file.
        logging.info("About to push package to cheese prism %s" % job_dict['remote'])

        p = Package(job_dict['package_name'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

        # Update the packages after an update. automatically add new version
        cache = Cache.cache()

        all_packages_as_json = cache.get("cheeseprism:packages")

        if all_packages_as_json:
            all_packages = json.loads(all_packages_as_json)

            for pckg in all_packages:
                if pckg["clean_name"] == comparable_name(job_dict['package_name']):
                    pckg["versions"].append(job_dict['version'])
                    break

            cache.set("cheeseprism:packages", dumps(all_packages))


        packages_as_json = cache.get('cheeseprism:package:' +
            comparable_name(job_dict['package_name']))

        if packages_as_json:
            packages = json.loads(packages_as_json)
            packages["versions"].append(job_dict['version'])
            packages_as_json = dumps(packages)

            cache.set('cheeseprism:package:' + job_dict['package_name'], packages_as_json)

        logging.info('Finished pushing package %s to CheesePrism' % job_dict['remote'])
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def cycle_services(config={}, job_dict={}):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'.
    It restarts the supervisor processes for a specific site.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('Cycling service %s' % job_dict['service'])

        for ip in job_dict['nodes']:
            logging.info('Cycling supervisord services: %s' %
                job_dict['supervisor_service_names'])

            for name in job_dict['supervisor_service_names']:
                logging.info('Cycling service %s on IP http://%s' % (name, ip))
                #http://stackoverflow.com/a/1766187/182484
                #set a global timeout on socket
                socket.setdefaulttimeout(30)
                Service.cycle(xmlrpclib.ServerProxy('http://' + ip + ':9001'), name)
                socket.setdefaulttimeout(None)

        logging.info('Done cycling %s' % job_dict['service'])
    except Exception as e:
        socket.setdefaulttimeout(None)
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

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

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

        # PUll the dev monkey repos data
        repos = pull_devmonkeys_repos()

        cache = Cache.cache()
        pipeline = cache.pipeline()

        for name, repo in repos.iteritems():
            key = "repo.devmonkeys:" + name
            pipeline.set(key, dumps(repo))

        pipeline.execute()

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

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

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

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
        log.info('%s pushed the following packages to %s: [%s]' %
                (job_dict['user_id'], job_dict['service_name'],
                ','.join(job_dict['packages'])))
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
                config['doula.assets.dir'],
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

        # Update this site by pulling the latest data for the site
        # Create a new job dict because we don't want logs mixed up
        pull_bambino_data_job_dict = {'id': uuid.uuid1().hex}
        pull_bambino_data(config, pull_bambino_data_job_dict)

        # Cycle the service after releasing the service
        cycle_services(config, job_dict)

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

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

        logging.info('Done pulling bambino data')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise


def job_expired(job):
    """
    Determines if a job on the queue has expired and needs to be
    pulled off the queue. For completed jobs it's 3 days, for failed or
    queued jobs it's 5 days
    """
    now = time.time()

    # The maintenance jobs always get popped off
    maintenance_job_types = [
        'cleanup_queue',
        'pull_cheeseprism_data',
        'pull_github_data',
        'pull_bambino_data',
        'pull_appenv_github_data',
        ]

    if job['job_type'] in maintenance_job_types:
        return True
    elif job['status'] == 'complete' and job['time_started'] < (now - 86400):
        # completed jobs stay on queue for 1 day
        return True
    elif job['time_started'] < (now - 172800):
        # failed and completed problems stay on queue for 2 days
        return True
    else:
        return False


def find_expired_jobs(jobs):
    """Find all the jobs on the queue that have expired"""
    return [job['id'] for job in jobs if job_expired(job)]


def cleanup_queue(config={}, job_dict={}):
    """
    Cleanup old jobs stored in our queueing system.
    """
    create_logger(job_dict['id'])
    load_config(config)

    try:
        logging.info('Cleaning up the queue')

        queue = Queue()
        expired_job_ids = find_expired_jobs(queue.get())

        queue.remove(expired_job_ids)

        # Remove all completed and failed logs
        for expired_job_id in expired_job_ids:
            path_to_file = os.path.join('/var/log/doula', expired_job_id + '.log')

            if os.path.isfile(path_to_file):
                os.remove(path_to_file)

        logging.info('Done cleaning up the queue')
    except Exception as e:
        logging.error(e.message)
        logging.error(traceback.format_exc())
        raise
