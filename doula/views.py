from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.services.cheese_prism import CheesePrism
from doula.util import dumps
from doula.util import git_dirify
from doula.util import to_log_msg
from git import GitCommandError
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import FileResponse
from pyramid.response import Response
from pyramid.view import view_config

import json
import logging
import os
import time
import traceback

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
# Service events
####################

@subscriber(ApplicationCreated)
def load_config(event):
    """
    Load the Service config settings
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
    tb = traceback.format_exc()

    return dumps({ 'success': False, 'msg': msg, 'stacktrace': tb })

def handle_exception(e, request):
    request.response.status = 500
    request.override_renderer = 'error/exception.html'
    log_error(e, e.message, request)
    tb = traceback.format_exc()

    return { 'msg': e.message, 'stacktrace': tb, 'config': Config }

def log_error(e, msg, request):
    tb = traceback.format_exc()
    print "TRACEBACK\n" + str(tb)

    log_vals = { 'url': request.url, 'error': msg, 'stacktrace': tb }
    log.error(to_log_msg(log_vals))
