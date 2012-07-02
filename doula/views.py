import os
import json
import time
import logging
import traceback

from doula.util import dumps
from doula.util import git_dirify
from doula.util import to_log_msg
from doula.models.sites_dal import SiteDAL
from doula.config import Config

from pyramid.response import FileResponse
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from git import GitCommandError

log = logging.getLogger('doula')

# SITE VIEWS
@view_config(route_name='home', renderer='sites/index.html')
def show_home(request):
    return show_sites(request)

@view_config(route_name='sites', renderer='sites/index.html')
def show_sites(request):
    """
    Show the testing sites
    """
    try:
        sites = SiteDAL.get_sites()
    except Exception as e:
        return handle_exception(e, request)

    return { 'sites': sites, 'config': Config }

@view_config(route_name='site', renderer="sites/site.html")
def site(request):
    try:
        site = get_site(request.matchdict['site_id'])
    except Exception as e:
        return handle_exception(e, request)

    return {
        'site': site, 
        'site_json': dumps(site), 
        'token': Config.get('token'),
        'config': Config
        }

@view_config(route_name='site_tag', renderer="string")
def site_tag(request):
    try:
        tag_history_path = Config.get('tag_history_path')
        tag_history_remote = Config.get('tag_history_remote')
        tag = git_dirify(request.POST['tag'])
        msg = request.POST['msg']

        site = get_site(request.POST['site_id'])
        # once we have user from ldap, pass that in
        site.tag(tag_history_path, tag_history_remote, tag, msg, 'anonymous')

        return dumps({'success': True, 'site_id': site})
    except GitCommandError as e:
        msg = "Git error: {0}." .format(str(e.stderr))
        return handle_json_exception(e, msg, request)
    except Exception as e:
        return handle_json_exception(e, msg, request)

###############
# SERVICE VIEWS
###############

@view_config(route_name='service', renderer="services/release_actions.html")
def service(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]
    except Exception:
        msg = 'Unable to find site and service under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['site_id'], request.matchdict['serv_id'])

        raise HTTPNotFound(msg)

    return { 'site': site, 'service': service, 'config': Config }


@view_config(route_name='service_details', renderer="services/service_details.html")
def service_details(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]
        
    except Exception:
        msg = 'Unable to find site and service under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['site_id'], request.matchdict['serv_id'])

        raise HTTPNotFound(msg)

    return { 'site': site, 'service': service, 'config': Config }

@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    try:
        service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])
        # todo, once we have a user logged in we'll pass in the user too
        tag = git_dirify(request.POST['tag'])
        service.tag(tag, request.POST['msg'], 'anonymous')

        # pull the updated service
        updated_service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])

        return dumps({ 'success': True, 'service': updated_service })
    except Exception as e:
        msg = 'Unable to tag site and service under "{0}" and "{1}"'
        msg = msg.format(request.POST['site_id'], request.POST['serv_id'])
        return handle_json_exception(e, msg, request)


@view_config(route_name='service_deploy', renderer="string")
def service_deploy(request):
    try:
        validate_token(request)

        service = SiteDAL.get_service(SiteDAL.get_master_site(), request.POST['serv_id'])
        tag = service.get_tag_by_name(request.POST['tag'])
        # todo, for now pass in the anonymous user until we start authenticating
        service.mark_as_deployed(tag, 'anonymous')

        return dumps({'success': True, 'service': service})
    except Exception as e:
        msg = 'Unable to deploy service. Error: "{0}"'
        msg = msg.format(e.message)
        return handle_json_exception(e, msg, request)

def validate_token(request):
    # Validate security token
    if(request.POST['token'] != Config.get('token')):
        raise Exception("Invalid security token")

def get_site(site_name):
    site = SiteDAL.get_site(site_name)

    if not site:
        msg = 'Unable to find site "{0}"'.format(site_name)
        raise HTTPNotFound(msg)

    return site

@view_config(route_name="service_freeze")
def service_freeze(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]

        response = Response(content_type='service/octet-stream')
        file_name = service.site_name + '_' + service.name_url + '_requirements.txt'
        response.content_disposition = 'attachment; filename="' + file_name + '"'
        response.charset = "UTF-8"
        response.text = service.freeze_requirements()
    except Exception as e:
        return handle_exception(e, request)

    return response

# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    return { 'config': Config }

# SETTINGS VIEWS
@view_config(route_name='settings', renderer='settings/index.html')
def show_settings(request):
    return { 'config': Config }

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

@view_config(route_name='bambino_ips', renderer="string")
def bambino_ips(request):
    """
    Return all the IP addresses for the Bambinos.
    Used for deployment to update every Bambino registered with Doula.
    """
    try:
        ips = SiteDAL.get_node_ips()
        return {'success': True, 'ip_addresses': ips}
    except KeyError as e:
        msg = 'Unable to find Bambino IP addresses "{0}"'
        msg = msg.format(request.POST['site_id'], request.POST['serv_id'])
        return handle_json_exception(e, msg, request)


####################
# Application events
####################

@subscriber(ApplicationCreated)
def load_config(event):
    """
    Load the Application config settings
    """
    Config.load_config(event.app.registry.settings)

@view_config(route_name='favicon')
def favicon_view(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, 'static', 'favicon.ico')
    return FileResponse(icon, request=request)

##################
# ERROR HANDLING
##################

@view_config(context=HTTPNotFound, renderer='error/404.html')
def not_found(self, request):
    request.response.status = 404
    log_error(request.exception, request.exception.message, request)

    return { 'msg': request.exception.message, 'config': Config }

def handle_json_exception(e, msg, request):
    request.response.status = 500
    log_error(e, msg, request)

    return dumps({ 'success': False, 'msg': msg, 'stacktrace': tb })

def handle_exception(e, request):
    request.response.status = 500
    request.override_renderer = 'error/exception.html'
    log_error(e, e.message, request)

    return { 'msg': e.message, 'stacktrace': tb, 'config': Config }

def log_error(e, msg, request):
    tb = traceback.format_exc()
    print "TRACEBACK\n" + str(tb)

    log_vals = { 'url': request.url, 'error': msg, 'stacktrace': tb }
    log.error(to_log_msg(log_vals))
