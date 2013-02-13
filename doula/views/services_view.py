from doula.cheese_prism import CheesePrism
from doula.config import Config
from doula.models.doula_dal import DoulaDAL
from doula.models.release import Release
from doula.models.release_dal import ReleaseDAL
from doula.queue import Queue
from doula.util import comparable_name
from doula.util import dumps
from doula.util import git_dirify
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
import json
import logging
import math
import time
import traceback
import pdb

log = logging.getLogger(__name__)

####################
# SERVICE INDEX VIEW
####################


@view_config(route_name='service', renderer="services/admin_actions.html")
def service(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])
    service = site.services[request.matchdict['service_name']]
    latest_service_config = service.get_configs()[0]

    releases = service.get_releases()
    last_release = get_last_release(releases, site.name)
    selected_release = last_release
    diff = last_release.diff_service_and_release(service)

    last_job = get_last_job(site, service)
    other_packages = CheesePrism.other_packages(service.packages)

    # show jobs in the past hour 8 hours
    jobs_started_after = math.floor(time.time() - (60 * 60 * 8))

    return {
        'site': site,
        'path': request.path,
        'service': service,
        'config': Config,
        'last_release': last_release,
        'latest_service_config': latest_service_config,
        'selected_release': selected_release,
        'last_job': last_job,
        'is_config_up_to_date': service.is_config_up_to_date(),
        'releases': releases,
        'diff': diff,
        'other_packages': other_packages,
        'queued_items': [],
        'jobs_started_after': jobs_started_after
    }


def get_last_release(releases, site_name):
    if len(releases) > 0:
        return releases[0]
    else:
        return Release.build_empty_release(site_name)

def get_last_job(site, service):
    """
    Return the last cycle or release_service job
    for this service
    """
    query = {
        'site': site.name,
        'service': service.name,
        'job_type': ['cycle_service', 'release_service', 'build_new_package']
    }

    queue = Queue()
    jobs = queue.find_jobs(query)

    last_job = None

    # Find the last job for this service. job must also be complete or failed
    # we don't want jobs that haven't completed as a status.
    for job in jobs:
        if job['status'] == 'queued':
            continue

        if last_job == None:
            last_job = job
        elif last_job['time_started'] < job['time_started']:
            last_job = job

    return last_job

####################
# DASHBOARD UPDATE
####################


@view_config(route_name='service_dashboard', renderer="string")
def service_dashboard(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])
    service = site.services[request.matchdict['service_name']]
    latest_service_config = service.get_configs()[0]
    releases = service.get_releases()
    last_release = get_last_release(releases, site.name)
    selected_release = last_release

    diff = last_release.diff_service_and_release(service)
    last_job = get_last_job(site, service)

    temp_data = {
        'site': site,
        'path': request.path,
        'service': service,
        'config': Config,
        'latest_service_config': latest_service_config,
        'last_release': last_release,
        'selected_release': selected_release,
        'diff': diff,
        'last_job': last_job,
        'is_config_up_to_date': service.is_config_up_to_date(),
    }

    return dumps({
        'success': True,
        'diff': diff,
        'squaresHTML': render('doula:templates/services/mini-dashboard-squares.html', temp_data),
        'configHTML': render('doula:templates/services/mini-dashboard-detail-config.html', temp_data),
        'releasesHTML': render('doula:templates/services/mini-dashboard-detail-releases.html', temp_data)
    })


@view_config(route_name='service_diff', renderer="string")
def service_diff(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])
    service = site.services[request.matchdict['service_name']]

    latest_service_config = service.get_configs()[0]
    releases = service.get_releases()
    last_release = get_last_release(releases, site.name)

    # alextodo.
    # Need to figure out if this is a reversion by doing a comparison against existing
    # releases. compare all packages and see. basically it would be doing a diff

    dict_data = {
        'date': request.POST['date'],
        'sha': request.POST['sha'],
        'packages': json.loads(request.POST['packages'])
    }

    selected_release = Release.build_release_on_the_fly(dict_data, service)

    diff = selected_release.diff_service_and_release(service)
    last_job = get_last_job(site, service)

    temp_data = {
        'site': site,
        'path': request.path,
        'service': service,
        'latest_service_config': latest_service_config,
        'config': Config,
        'last_release': last_release,
        'selected_release': selected_release,
        'diff': diff,
        'last_job': last_job,
        'is_config_up_to_date': service.is_config_up_to_date(),
    }

    return dumps({
        'success': True,
        'diff': diff,
        'squaresHTML': render('doula:templates/services/mini-dashboard-squares.html', temp_data),
        'configHTML': render('doula:templates/services/mini-dashboard-detail-config.html', temp_data),
        'releasesHTML': render('doula:templates/services/mini-dashboard-detail-releases.html', temp_data)
    })

############
# Release
############

@view_config(route_name='service_release', renderer="string")
def service_release(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])

    if site.is_locked():
        msg = "This site is locked. Contact devops@surveymonkey.com"
        return dumps({'success': False, 'msg': msg})

    service = dd.find_service_by_name(
                request.matchdict['site_name'],
                request.matchdict['service_name'])

    packages = json.loads(request.POST['packages'])

    job_id = enqueue_release_service(request, service, packages, request.POST['sha'])

    return dumps({'success': True, 'job_id': job_id})


def enqueue_release_service(request, service, packages, sha):
    """
    Enqueue the job onto the queue
    """
    manifest = build_release_manifest(request, service, packages, sha)

    return Queue().enqueue({
        "job_type": "release_service",
        "service": service.name,
        "site": service.site_name,
        "user_id": request.user['username'],
        "manifest": manifest
    })


def build_release_manifest(request, service, packages, sha):
    """
    Build a release manifest for the next release
    # alextodo. we would send a release ID if we were reverting
    # alextodo. will need to calculate if this is a rollback. we will not count
    # on a release number. we will determine if it's a rollback. then we
    # will find that release number

    # once we know if it's a release we're golden. then 'were done'
    """
    return {
        "is_rollback": False,
        "service": service.name,
        "site": service.site_name,
        "author": request.user['username'],
        "packages": packages,
        "sha1_etc": sha,
        "comparable_packages": build_comparable_packages(packages)
    }


def build_comparable_packages(packages):
    """
    Build the comparable packages
    """
    comparable_packages = {}

    for name, version in packages.iteritems():
        comparable_packages[comparable_name(name)] = version

    return comparable_packages

############
# Cycle
############

@view_config(route_name='service_cycle', renderer="string")
def service_cycle(request):
    try:
        dd = DoulaDAL()
        service = dd.find_service_by_name(
                    request.matchdict['site_name'],
                    request.matchdict['service_name'])

        job_id = enqueue_cycle_service(request, service)
    except Exception as e:
        msg = 'Error attempting to cycle %s' % request.matchdict['service_name']
        log.error(e.message)
        log.error(traceback.format_exc())

        return dumps({'success': False, 'msg': msg})

    return dumps({'success': True, 'job_id': job_id})


def enqueue_cycle_service(request, service):
    """
    Enqueue the cycle services job onto the queue
    """
    return Queue().enqueue({
        'job_type': 'cycle_service',
        'service': service.name,
        'site': service.site_name,
        'user_id': request.user['username']
    })

###############
# Production
###############

@view_config(route_name='deployed_to_production', renderer="string")
def deployed_to_production(request):
    # alextodo. mark as deployed to prod here.
    # will need to mark the service.
    # todo: what do we need passed in?
    # who do we need to call locally?

    # What we're sending to kael right now is. a tag. that's all he needs. no?

    rdal = ReleaseDAL()
    manifest = rdal.find_manifest_by_release_number(site_name, service_name, release_number)

    return dumps({'success': True})