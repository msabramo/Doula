import json
import time
import logging
import traceback

from doula.queue.release_queue import start_release_queue
from doula.util import dumps
from doula.util import git_dirify
from doula.models.sites_dal import SiteDAL
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from git import GitCommandError

log = logging.getLogger('doula')

# ENVIRONMENT VIEWS
@view_config(route_name='home', renderer='envs/index.html')
def show_home(request):
    return show_envs(request)

@view_config(route_name='envs', renderer='envs/index.html')
def show_envs(request):
    """
    Show the testing environments in SM environment
    """
    return { 'envs': SiteDAL.get_environments() }


# BELOW THIS LINE NEEDS PORTING OVER TO NEW ISH

@view_config(route_name='environment', renderer="envs/environment.html")
def environment(request):
    site = get_site(request.matchdict['site'])
    token = request.registry.settings['token']

    return {'site': site, 'site_json': dumps(site), 'token': token}

@view_config(route_name='environment_tag', renderer="string")
def environment_tag(request):
    try:
        # alextodo, should I simply create a config global object and access that
        # instead of reading all the time from registry? that would be testable too
        # better than this. talk to whit.
        tag_history_path = request.registry.settings['tag_history_path']
        tag_history_remote = request.registry.settings['tag_history_remote']
        tag = git_dirify(request.POST['tag'])
        msg = request.POST['msg']

        site = get_site(request.POST['site'])
        # once we have user from ldap, pass that in
        site.tag(tag_history_path, tag_history_remote, tag, msg, 'anonymous')

        return dumps({'success': True, 'site': site})
    except GitCommandError as e:
        msg = "Git error: {0}." .format(str(e.stderr))
        return dumps({'success': False, 'msg': msg})
    except Exception as e:
        tb = traceback.format_exc()
        print 'TRACEBACK'
        print tb
        msg = 'Error: {0}'.format(e.message)

        return dumps({'success': False, 'msg': msg})

# SERVICE VIEWS

@view_config(route_name='service', renderer="service/index.html")
def service(request):
    try:
        site = get_site(request.matchdict['site'])
        app = site.applications[request.matchdict['application']]

    except Exception:
        msg = 'Unable to find site and application under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['site'], request.matchdict['application'])

        raise HTTPNotFound(msg)

    return {'site': site, 'app': app}


@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    try:
        app = SiteDAL.get_application(request.POST['site'], request.POST['application'])
        # todo, once we have a user logged in we'll pass in the user too
        tag = git_dirify(request.POST['tag'])
        app.tag(tag, request.POST['msg'], 'anonymous')

        return dumps({'success': True, 'app': app})
    except KeyError:
        msg = 'Unable to tag site and application under "{0}" and "{1}"'
        msg = msg.format(request.POST['site'], request.POST['application'])

        return dumps({'success': False, 'msg': msg})


@view_config(route_name='service_deploy', renderer="string")
def service_deploy(request):
    try:
        validate_token(request)

        app = SiteDAL.get_application(SiteDAL.get_master_site(), request.POST['application'])
        tag = app.get_tag_by_name(request.POST['tag'])
        # todo, for now pass in the anonymous user until we start authenticating
        app.mark_as_deployed(tag, 'anonymous')

        return dumps({'success': True, 'app': app})
    except Exception as e:
        msg = 'Unable to deploy application. Error: "{0}"'
        msg = msg.format(e.message)
        log.error(msg)

        return dumps({'success': False, 'msg': msg})

def validate_token(request):
    # Validate security token
    if(request.POST['token'] != request.registry.settings['token']):
        raise Exception("Invalid security token")

def get_site(site_name):
    site = SiteDAL.get_site(site_name)

    if not site:
        msg = 'Unable to find site "{0}"'.format(site_name)
        raise HTTPNotFound(msg)

    return site

@view_config(route_name="service_freeze")
def service_freeze(request):
    site = get_site(request.matchdict['site'])
    app = site.applications[request.matchdict['application']]

    response = Response(content_type='application/octet-stream')
    file_name = app.site_name + '_' + app.name_url + '_requirements.txt'
    response.content_disposition = 'attachment; filename="' + file_name + '"'
    response.charset = "UTF-8"
    response.text = app.freeze_requirements()

    return response

# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    return {}

# SETTINGS VIEWS
@view_config(route_name='settings', renderer='settings/index.html')
def show_settings(request):
    return {}

# BAMBINO VIEWS
@view_config(route_name='bambino_register', renderer='json')
def bambino_register(request):
    """
    Register a Bambino node with Doula.
    """
    node = json.loads(request.POST['node'])
    node['time'] = time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime())

    if(request.POST['action'] == 'register'):
        SiteDAL.register_node(node)
    else:
        SiteDAL.unregister_node(node)

    return {'success': 'true'}

@view_config(route_name='bambino_ips', renderer="json")
def bambino_ips(request):
    """
    Return all the IP addresses for the Bambinos.
    Used for deployment to update every Bambino registered with Doula.
    """
    try:
        ips = SiteDAL.get_node_ips()
        return {'success': True, 'ip_addresses': ips}
    except KeyError:
        msg = 'Unable to find Bambino IP addresses "{0}"'
        msg = msg.format(request.POST['site'], request.POST['application'])

        return dumps({'success': False, 'msg': msg})

# ERROR HANDLING
@view_config(context=HTTPNotFound, renderer='error/404.html')
def not_found(self, request):
    request.response.status = 404

    return {'msg': request.exception.message}