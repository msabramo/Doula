from doula.cheese_prism import CheesePrism
from doula.config import Config
from doula.models.doula_dal import DoulaDAL
from doula.queue import Queue
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

log = logging.getLogger(__name__)

####################
# SERVICE INDEX VIEW
####################


@view_config(route_name='service', renderer="services/admin_actions.html")
def service(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])
    service = site.services[request.matchdict['service_name']]
    releases = service.get_releases()
    last_release = get_last_release(releases)
    last_job = get_last_job(site, service)

    other_packages = CheesePrism.other_packages(service.packages)
    # show jobs in the past hour 8 hours
    jobs_started_after = math.floor(time.time() - (60 * 60 * 8))

    return {
        'site': site,
        'service': service,
        'config': Config,
        'last_release': last_release,
        'last_job': last_job,
        'is_config_up_to_date': service.is_config_up_to_date(),
        'service_json': dumps(service),
        'releases_json': dumps(releases),
        'other_packages': other_packages,
        'queued_items': [],
        'jobs_started_after': jobs_started_after
    }


def get_last_release(releases):
    if len(releases) > 0:
        return releases[0]
    else:
        return None


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
    jobs = queue.get(query)

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
    releases = service.get_releases()
    last_release = get_last_release(releases)
    last_job = get_last_job(site, service)

    temp_data = {
        'site': site,
        'service': service,
        'config': Config,
        'last_release': last_release,
        'last_job': last_job,
        'is_config_up_to_date': service.is_config_up_to_date(),
    }

    return dumps({
        'success': True,
        'squaresHTML': render('doula:templates/services/mini-dashboard-squares.html', temp_data),
        'configHTML': render('doula:templates/services/mini-dashboard-detail-config.html', temp_data),
        'releasesHTML': render('doula:templates/services/mini-dashboard-detail-releases.html', temp_data)
    })

####################
# Service Details
####################


@view_config(route_name='service_details', renderer="services/service_details.html")
def service_details(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])
    service = site.services[request.matchdict['service_name']]

    return {'site': site, 'service': service, 'config': Config}


@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    dd = DoulaDAL()
    service = dd.find_service_by_name(
                request.matchdict['site_name'],
                request.matchdict['service_name'])

    tag = git_dirify(request.POST['tag'])
    service.tag(tag, request.POST['msg'], request.user['username'])

    return dumps({'success': True, 'service': service})


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

    job_id = enqueue_release_service(request, service, packages)

    return dumps({'success': True, 'job_id': job_id})


def enqueue_release_service(request, service, packages):
    """
    Enqueue the job onto the queue
    """
    pckgs = []

    for name, version in packages.iteritems():
        pckgs.append(name + '==' + version)

    q = Queue()

    # todo: use service and service_name
    job_id = q.this({
        'job_type': 'release_service',
        'packages': pckgs,
        'service': service.name,
        'site': service.site_name,
        'user_id': request.user['username']
    })

    # After we push the release. lets pull the latest release data again.
    # alextodo. after big rewrite just make it work correctly with this info.
    q.this({
        'job_type': 'pull_appenv_github_data'
    })

    return job_id


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
        log.error(msg)
        log.error(e.message)
        log.error(traceback.format_exc())

        return dumps({'success': False, 'msg': msg})

    return dumps({'success': True, 'job_id': job_id})


def enqueue_cycle_service(request, service):
    """
    Enqueue the cycle services job onto the queue
    """
    return Queue().this({
        'job_type': 'cycle_service',
        'service': service.name,
        'site': service.site_name,
        'user_id': request.user['username']
    })


@view_config(route_name="service_freeze")
def service_freeze(request):
    dd = DoulaDAL()
    service = dd.find_service_by_name(
                request.matchdict['site_name'],
                request.matchdict['service_name'])

    response = Response(content_type='service/octet-stream')
    file_name = service.site_name + '_' + service.name_url + '_requirements.txt'
    response.content_disposition = 'attachment; filename="' + file_name + '"'
    response.charset = "UTF-8"
    response.text = unicode(service.freeze_requirements())

    return response


