from doula.cache import Redis
from doula.cheese_prism import CheesePrism
from doula.config import Config
from doula.github import pull_appenv_repos
from doula.github import pull_devmonkeys_repos
from doula.models.package import Package
from doula.models.push import Push
from doula.models.service import Service
from doula.models.doula_dal import DoulaDAL
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


#####################
# User Initiated Jobs
#####################

def build_new_package(config={}, job_dict={}):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'build_new_package'.  Upon being called, it will
    updated the version present in the setup.py of the repo, and release the
    package to cheeseprism.
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        vals = (job_dict['comparable_name'], job_dict['version'])
        log.info("Pushing package '%s' with version %s to CheesePrism" % vals)

        p = Package(job_dict['package_name'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

        # Update the packages after an update. automatically add new version
        redis = Redis.get_instance()

        all_packages_as_json = redis.get("cheeseprism:packages")

        if all_packages_as_json:
            all_packages = json.loads(all_packages_as_json)

            for pckg in all_packages:
                if pckg["comparable_name"] == job_dict['comparable_name']:
                    pckg["versions"].append(job_dict['version'])
                    break

            redis.set("cheeseprism:packages", dumps(all_packages))

        packages_as_json = redis.get('cheeseprism:package:' + job_dict['comparable_name'])

        if packages_as_json:
            packages = json.loads(packages_as_json)
            packages["versions"].append(job_dict['version'])
            packages_as_json = dumps(packages)

            redis.set('cheeseprism:package:' + job_dict['comparable_name'], packages_as_json)

        log.info('Finished pushing package %s to CheesePrism' % job_dict['remote'])
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def cycle_service(config={}, job_dict={}):
    """
    This job restarts the supervisord processes for the service on the site
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        log.info('Cycling %s on %s' % (job_dict['service'], job_dict['site']))

        dd = DoulaDAL()
        service = dd.find_service_by_name(job_dict['site'], job_dict['service'])

        # Roll through all the nodes for this service
        for node_name, node in service.nodes.iteritems():
            vals = (service.name, node.ip)
            msg = "Cycling supervisord services '%s' on node with IP %s" % vals
            log.info(msg)

            for supervisor_service_name in node.supervisor_service_names:
                log.info("Cycling supervisord service with name '%s'" %
                    supervisor_service_name)

                # Supervisord doesn't have a default timeout, it will just hang
                # Solution is to set a global timeout on socket,
                # then set it back to default
                # See original soloution here: http://stackoverflow.com/a/1766187/182484

                # Set the timeout to 30 seconds
                socket.setdefaulttimeout(30)
                url = 'http://' + node.ip + ':9001'
                Service.cycle(xmlrpclib.ServerProxy(url), supervisor_service_name)

                # Set the timeout back to default
                socket.setdefaulttimeout(None)

            log.info('Done cycling services on node with IP %s' % node.ip)

        log.info('Done cycling %s on %s' % (job_dict['service'], job_dict['site']))
    except Exception as e:
        socket.setdefaulttimeout(None)
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def release_service(config={}, job_dict={}, debug=False):
    """
    Release a service to a specific site.
    1) Pip install the packages sent
    2) Update config files
    3) Cycle the services
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        dd = DoulaDAL()
        service = dd.find_service_by_name(job_dict['site'], job_dict['service'])

        vals = (','.join(job_dict['packages']), service.name, service.site_name)
        log.info('Pushing the packages %s to %s on %s.' % vals)

        failures = []
        successes = []

        try:
            # Roll through all the nodes for this service and push
            # the packages for each node in the service
            for node_name, node in service.nodes.iteritems():
                vals = (service.name, node.ip)
                msg = "Pushing %s to the node with IP %s" % vals
                log.info(msg)

                push = Push(
                    service.name,
                    node.ip,
                    job_dict['user_id'],
                    config['bambino.webapp_dir'],
                    config['doula.cheeseprism_url'],
                    config['doula.keyfile_path'],
                    config['doula.assets.dir'],
                    debug
                )

            successes, failures = push.packages(job_dict['packages'])
        except Exception as e:
            print 'EXCEPTION IN JOB:'
            # getting this message. sequence item 0: exp
            print e.message

            failures.append({'package': 'git', 'error': str(e)})

        if failures:
            # timtodo. this used to use join, failures returns this
            # [{'error': "'bambino.web_app_dir'", 'package': 'git'}]
            # Old call. this is here
            # raise Exception(','.join(failures['error']))
            raise Exception(failures[0]['error'])

        logging.getLogger().setLevel(logging.INFO)
        create_logger(job_dict['id'])
        log.info('Done installing packages.')

        # Update this site by pulling the latest data for the site
        # Create a new job dict because we don't want logs mixed up
        # This will update the config related informaton.
        pull_bambino_data_job_dict = {'id': uuid.uuid1().hex}
        pull_bambino_data(config, pull_bambino_data_job_dict)

        # Pull the latest app env data as well
        # Create a new job dict because we don't want to mix the logs
        # This will update the releases related ata
        pull_appenv_github_data_job_dict = {'id': uuid.uuid1().hex}
        # alextodo. speed this up to. it's fucked on prod. so fix it.
        pull_appenv_github_data(config, pull_appenv_github_data_job_dict)

        # Cycle the service after releasing the service
        cycle_service(config, job_dict)

        return successes, failures
    except Exception as e:
        logging.getLogger().setLevel(logging.INFO)
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


########################
# Doula Maintenance Jobs
########################

def pull_cheeseprism_data(config={}, job_dict={}):
    """
    Ping Cheese Prism and pull the latest packages and all of their versions.
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        log.info('Started pulling cheeseprism data')

        redis = Redis.get_instance()
        pipeline = redis.pipeline()

        packages = CheesePrism.pull_all_packages()
        pipeline.set("cheeseprism:packages", dumps(packages))

        for pckg in packages:
            pipeline.set('cheeseprism:package:' + pckg.comparable_name, dumps(pckg))

        pipeline.execute()

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

        log.info('Done pulling data from cheeseprism')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_github_data(config={}, job_dict={}):
    """
    Pull the github data for every python package.
    Pull commit history, tags, branches. Everything.

    # alextodo. this is the slowest call we have. 60 seconds. speed it up.
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        start = time.time()
        log.info('pulling github data')

        # PUll the dev monkey repos data
        repos = pull_devmonkeys_repos()

        redis = Redis.get_instance()
        pipeline = redis.pipeline()

        # Clear the elements in the set by deleting the key
        pipeline.delete("repo.devmonkeys")

        for name, repo in repos.iteritems():
            pipeline.sadd("repo.devmonkeys", name)
            key = "repo.devmonkeys:" + name
            pipeline.set(key, dumps(repo))

        pipeline.execute()

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

        diff = time.time() - start
        print "\n"
        print 'DIFF IN TIME FOR PULL GITHUB DATA: ' + str(diff)

        log.info('Done pulling github data')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_appenv_github_data(config={}, job_dict={}, debug=False):
    """
    Pull the github data for every App environment
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        start = time.time()
        log.info('Pulling github appenv data')
        redis = Redis.get_instance()
        repos = pull_appenv_repos()
        redis.set("repos:appenvs", dumps(repos))

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

        diff = time.time() - start
        print "\n"
        print 'DIFF IN TIME FOR PULL APPENV: ' + str(diff)

        log.info('Done pulling github appenv data')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_bambino_data(config={}, job_dict={}):
    """
    Pull the data from all the bambino's
    """
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        start = time.time()
        log.info('Pulling bambino data')

        dd = DoulaDAL()
        dd.update_site_and_service_models()

        # always remove maintenance jobs from the queue
        Queue().remove(job_dict['id'])

        diff = time.time() - start
        print "\n"
        print 'DIFF IN TIME FOR PULL BAMBINO DATA: ' + str(diff)

        log.info('Done pulling bambino data')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
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
    log = create_logger(job_dict['id'])
    load_config(config)

    try:
        log.info('Cleaning up the queue')

        queue = Queue()
        expired_job_ids = find_expired_jobs(queue.get())

        queue.remove(expired_job_ids)

        # Remove all completed and failed logs
        for expired_job_id in expired_job_ids:
            path_to_file = os.path.join('/var/log/doula', expired_job_id + '.log')

            if os.path.isfile(path_to_file):
                os.remove(path_to_file)

        log.info('Done cleaning up the queue')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise
