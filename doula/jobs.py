from doula.cache import Cache
from doula.github.github import pull_devmonkeys_repos
from doula.models.package import Package
from doula.models.node import Node
from doula.models.service import Service
from doula.models.sites_dal import SiteDAL
from doula.services.cheese_prism import CheesePrism
from doula.util import *
import logging
import sys
import traceback
import xmlrpclib

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fh = logging.FileHandler('/var/log/doula/jobs.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
log.addHandler(ch)


def push_to_cheeseprism(job_dict=None):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'push_to_cheeseprism'
    joetodo be descriptive about what the task actually does.
    """
    try:
        # alextodo, figure out how the hell retools works. wtf.
        log.info("About to push package to cheese prism %s" % job_dict['remote'])

        p = Package(job_dict['service'], '0', job_dict['remote'])
        p.distribute(job_dict['branch'], job_dict['version'])

        log.info('Finished pushing package %s to CheesePrism' % job_dict['remote'])
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def cycle_services(supervisor_ip, service_name):
    """
    This function will be enqueued by Queue upon receiving a job dict that
    has a job_type of 'cycle_services'
    joetodo be descriptive about what the task actually does.
    """
    try:
        log.info('started cycling service %s' % service_name)

        Service.cycle(xmlrpclib.ServerProxy(supervisor_ip), service_name)
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_cheeseprism_data(job_dict):
    """
    Ping Cheese Prism and pull the latest packages and all of their versions.
    """
    try:
        log.info('Started pulling cheeseprism data')

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


def pull_github_data(job_dict):
    """
    Pull the github data for every python package.
    Pull commit history, tags, branches. Everything.
    """
    try:
        log.info('pulling github data')

        repos = pull_devmonkeys_repos()
        cache = Cache.cache()
        cache.set("devmonkeys_repos", dumps(repos))

        log.info('Done pulling github data')
    except Exception as e:
        log.error(e.message)
        log.error(traceback.format_exc())
        raise


def pull_bambino_data(job_dict):
    """
    Pull the data from all the bambino's
    """
    try:
        log.info('Pulling bambino data')

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
