from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.queue import Queue
from doula.services.cheese_prism import CheesePrism
from doula.util import *
from doula.views.helpers import *
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
from datetime import datetime
import time
import logging
import re

log = logging.getLogger(__name__)

###############
# SERVICE VIEWS
###############


@view_config(route_name='service', renderer="services/release_actions.html")
def service(request):
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]
    other_packages = CheesePrism.other_packages(service.packages)

    query = {'job_type': ['push_to_cheeseprism', 'cycle_services', 'push_service_environment'],
             'service': service.name}
    last_updated = datetime.now()
    last_updated = time.mktime(last_updated.timetuple())

    return {
        'site': site,
        'service': service,
        'config': Config,
        'service_json': dumps(service),
        'releases_json': dumps(service.get_releases()),
        'other_packages': other_packages,
        'queued_items': [],
        'last_updated': last_updated,
        'job_dict': dumps(query)
    }


@view_config(route_name='service_cheese_prism_modal', renderer="services/modal_push_package.html")
def service_cheese_prism_modal(request):
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]
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
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]
    package = service.get_package_by_name(request.GET['name'])

    remote = package.get_github_info()['ssh_url']
    next_version = request.GET['next_version']
    branch = request.GET['branch']

    # alextodo, use a validation for the branch and version right here
    # no empty values, no duplicates, make sure the branch exist
    # alextodo, verification will also require that we don't allow
    # another version number that is already being pushed onto the queue
    errors = validate_release(package, branch, next_version)

    if len(errors) == 0:
        job_dict = enqueue_push_package(request.user['username'],
                                        service,
                                        remote,
                                        branch,
                                        next_version)
    else:
        msg = "There were errors attempting to release %s" % (service.name)
        html = render('doula:templates/services/release_package_error.html',
                {'msg': msg, 'errors': errors})

        return dumps({'success': False, 'msg': msg, 'html': html})

    return dumps({'success': True, 'job': job_dict})


def validate_release(package, branch, next_version):
    """
    Validate that:
        The version number does not already exist
        alextodo, we need to figure out if the version number has already
        been added to the queue, check against that too
    """
    errors = []
    git_info = package.get_github_info()

    if not next_version:
        errors.add('Version number cannot be empty')

    for tag in git_info['tags']:
        # tags by doula are always prefixed with a v
        # and test that it doesn't match without
        tag_name = re.sub(r'^v', '', str(tag['name']))

        if tag_name == next_version:
            msg = "This package version (%s) already exist. "
            msg += "Try another version."
            msg = msg % next_version
            errors.append(msg)

    return errors


def enqueue_push_package(user_id, service, remote, branch, version):
    """
    Enqueue the job onto the queue
    """
    job_dict = {
        'user_id': user_id,
        'site': service.site_name,
        'service': service.name,
        'remote': remote,
        'branch': branch,
        'version': version,
        'job_type': 'push_to_cheeseprism'
    }
    q = Queue()
    q.this(job_dict)

    return job_dict


@view_config(route_name='service_details', renderer="services/service_details.html")
def service_details(request):
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]

    return {'site': site, 'service': service, 'config': Config}


@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])
    # todo, once we have a user logged in we'll pass in the user too
    tag = git_dirify(request.POST['tag'])
    service.tag(tag, request.POST['msg'], 'anonymous')

    # pull the updated service
    updated_service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])

    return dumps({'success': True, 'service': updated_service})


@view_config(route_name='service_deploy', renderer="string")
def service_deploy(request):
    validate_token(request)

    service = SiteDAL.get_service(SiteDAL.get_master_site(), request.POST['serv_id'])
    tag = service.get_tag_by_name(request.POST['tag'])
    # todo, for now pass in the anonymous user until we start authenticating
    service.mark_as_deployed(tag, 'anonymous')

    return dumps({'success': True, 'service': service})


def validate_token(request):
    # Validate security token
    if(request.POST['token'] != Config.get('token')):
        raise Exception("Invalid security token")


@view_config(route_name='service_release', renderer="string")
def service_release(request):
    # alextodo. use a get from request call
    service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])
    nodes = SiteDAL.nodes(service.site_name)

    packages = json.loads(request.POST['packages'])
    job_id = enqueue_service_release(request, nodes, service, packages)

    return dumps({'success': True, 'job_id': job_id})


def enqueue_service_release(request, nodes, service, packages):
    """
    Enqueue the job onto the queue
    """

    if Config.get('env') == 'prod':
        ip = ''

        # alextodo, take a look at this. is it ever more than one?
        # if not deal with that
        for node_name in nodes:
            nodes[node_name]['ip']
            break
    else:
        ip = Config.get('doula.deploy.site')

    pckgs = []

    for name, version in packages.iteritems():
        pckgs.append(name + '==' + version)

    # alextodo. make a call to
    # UPDATE THE SERVICES FOR THE RELEASES
    # make a call to pull_appenv_github_data
    print 'IP OR SITE NAME'
    print ip

    queue = Queue()

    return queue.this({
        'user_id': request.user['username'],
        'job_type': 'push_service_environment',
        'site_name_or_node_ip': ip,
        'service_name': service.name,
        'packages': pckgs
    })


@view_config(route_name='service_cycle', renderer="string")
def service_cycle(request):
    service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])
    nodes = SiteDAL.nodes(service.site_name)
    job_id = enqueue_cycle_services(request, nodes, service)

    return dumps({'success': True, 'job_id': job_id})


def enqueue_cycle_services(request, nodes, service):
    """
    Enqueue the job onto the queue
    """
    # alextodo, make sure to account for the problem where
    # a service could be spread across several boxes
    # you would need to be able to restart all of them, do we abstract this?
    # make sure all the nodes service's are in the supervisord_service_names
    ips = []

    for node_name in nodes:
        ips.append(nodes[node_name]['ip'])

    queue = Queue()

    return queue.this({
        'user_id': request.user['username'],
        'job_type': 'cycle_services',
        'site': service.site_name,
        'nodes': ips,
        'service': service.name,
        'supervisor_service_names': service.supervisor_service_names
    })


@view_config(route_name="service_freeze")
def service_freeze(request):
    site = get_site(request.matchdict['site_id'])
    service = site.services[request.matchdict['serv_id']]

    response = Response(content_type='service/octet-stream')
    file_name = service.site_name + '_' + service.name_url + '_requirements.txt'
    response.content_disposition = 'attachment; filename="' + file_name + '"'
    response.charset = "UTF-8"
    response.text = service.freeze_requirements()

    return response
