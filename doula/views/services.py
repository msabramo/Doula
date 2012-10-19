from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.queue import Queue
from doula.cheese_prism import CheesePrism
from doula.util import *
from doula.views.helpers import *
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
import math
import logging
import re
import time

log = logging.getLogger(__name__)

###############
# SERVICE VIEWS
###############


@view_config(route_name='service', renderer="services/release_actions.html")
def service(request):
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]
    other_packages = CheesePrism.other_packages(service.packages)
    # show jobs in the past hour 8 hours
    jobs_started_after = math.floor(time.time() - (60 * 60 * 8))

    return {
        'site': site,
        'service': service,
        'config': Config,
        'service_json': dumps(service),
        'releases_json': dumps(service.get_releases()),
        'other_packages': other_packages,
        'queued_items': [],
        'jobs_started_after': jobs_started_after
    }


@view_config(route_name='service_cheese_prism_modal',
    renderer="services/modal_push_package.html")
def service_cheese_prism_modal(request):
    service = get_service_from_url(request)
    package = service.get_package_by_name(request.GET['name'])

    versions = package.get_versions()
    versions.sort()
    versions.reverse()
    current_version = versions[0]

    return {
        'service': service,
        'package': package,
        'current_version': current_version,
        'next_version': next_version(current_version)
    }


@view_config(route_name='service_cheese_prism_push', renderer="string")
def service_cheese_prism_push(request):
    service = get_service_from_url(request)
    package = service.get_package_by_name(request.GET['name'])

    branch = request.GET['branch']
    # The next version number is a combination of the actual version
    # number and the name of the actual branch
    next_version = request.GET['next_version'] + '-' + branch
    remote = package.get_github_info()['ssh_url']

    errors = validate_package_release(package, branch, next_version)

    if len(errors) == 0:
        job_dict = enqueue_push_package(request.user['username'],
                                        service,
                                        package,
                                        remote,
                                        branch,
                                        next_version)
    else:
        msg = "There were errors attempting to release %s" % (service.name)
        html = render('doula:templates/services/release_package_error.html',
                {'msg': msg, 'errors': errors})

        return dumps({'success': False, 'msg': msg, 'html': html})

    return dumps({'success': True, 'job': job_dict})


def validate_package_release(package, branch, next_version):
    """
    Validate that:
        The version number does not already exists
    """
    errors = []
    git_info = package.get_github_info()

    if not next_version:
        errors.append('Version number cannot be empty')

    if next_version.find('@') > -1:
        errors.append('You cannot include the "@" symbol in a version')

    for tag in git_info['tags']:
        # tags by doula are always prefixed with a v
        # and test that it doesn't match without
        tag_name = re.sub(r'^v', '', str(tag['name']))

        if tag_name == next_version:
            msg = "This package version (%s) already exists. "
            msg += "Try another version."
            msg = msg % next_version
            errors.append(msg)

    return errors


def enqueue_push_package(user_id, service, package, remote, branch, version):
    """
    Enqueue the job onto the queue
    """
    job_dict = {
        'user_id': user_id,
        'site': service.site_name,
        'service': service.name,
        'package_name': package.name,
        'remote': remote,
        'branch': branch,
        'version': version,
        'job_type': 'push_to_cheeseprism'
    }

    q = Queue()
    job_id = q.this(job_dict)
    job_dict['id'] = job_id

    return job_dict


@view_config(route_name='service_details', renderer="services/service_details.html")
def service_details(request):
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]

    return {'site': site, 'service': service, 'config': Config}


@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    service = get_service_from_url(request)
    tag = git_dirify(request.POST['tag'])
    service.tag(tag, request.POST['msg'], request.user['username'])

    # pull the updated service
    updated_service = get_service_from_url(request)

    return dumps({'success': True, 'service': updated_service})


@view_config(route_name='service_deploy', renderer="string")
def service_deploy(request):
    validate_token(request)

    service = SiteDAL.get_service(SiteDAL.get_master_site(), request.POST['serv_id'])
    tag = service.get_tag_by_name(request.POST['tag'])
    service.mark_as_deployed(tag, request.user['username'])

    return dumps({'success': True, 'service': service})


def validate_token(request):
    # Validate security token
    if(request.POST['token'] != Config.get('token')):
        raise Exception("Invalid security token")


@view_config(route_name='service_release', renderer="string")
def service_release(request):
    site = get_site(request.matchdict['site_id'])

    if site.is_locked():
        msg = "This site is locked. Contact devops@surveymonkey.com"
        return dumps({'success': False, 'msg': msg})

    service = get_service_from_url(request)
    packages = json.loads(request.POST['packages'])

    job_id = enqueue_release_service(request, service, packages)

    return dumps({'success': True, 'job_id': job_id})


def enqueue_release_service(request, service, packages):
    """
    Enqueue the job onto the queue
    """
    if Config.get('env') == 'prod':
        nodes = SiteDAL.nodes(service.site_name)
        # alextodo. move to multinodes now
        ips = [nodes[service.node_name]["ip"]]
    else:
        ips = Config.get('doula.deploy.site')

    pckgs = []

    for name, version in packages.iteritems():
        pckgs.append(name + '==' + version)

    q = Queue()

    job_id = q.this({
        'job_type': 'push_service_environment',
        'nodes': [ips],
        'packages': pckgs,
        'service': service.name,
        'service_name': service.name,
        'site': service.site_name,
        'site_name_or_node_ip': ips,
        'supervisor_service_names': service.supervisor_service_names,
        'user_id': request.user['username']
    })

    # After we push the release. lets pull the latest release data again.
    q.this({
        'job_type': 'pull_appenv_github_data'
    })

    return job_id


@view_config(route_name='service_cycle', renderer="string")
def service_cycle(request):
    service = get_service_from_url(request)
    nodes = SiteDAL.nodes(service.site_name)
    job_id = enqueue_cycle_services(request, nodes, service)

    return dumps({'success': True, 'job_id': job_id})


def enqueue_cycle_services(request, nodes, service):
    """
    Enqueue the job onto the queue
    """
    # Pull the ip address of the node where the service lives
    ips = [nodes[service.node_name]["ip"]]

    return Queue().this({
        'job_type': 'cycle_services',
        'nodes': ips,
        'service': service.name,
        'site': service.site_name,
        'supervisor_service_names': service.supervisor_service_names,
        'user_id': request.user['username']
    })


@view_config(route_name="service_freeze")
def service_freeze(request):
    service = get_service_from_url(request)

    response = Response(content_type='service/octet-stream')
    file_name = service.site_name + '_' + service.name_url + '_requirements.txt'
    response.content_disposition = 'attachment; filename="' + file_name + '"'
    response.charset = "UTF-8"
    response.text = service.freeze_requirements()

    return response


def get_service_from_url(request):
    """
    Get the service using the two params from the URL
        site_id and serv_id
    """
    return SiteDAL.get_service(
        request.matchdict['site_id'],
        request.matchdict['serv_id'])
