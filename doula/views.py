import json
import time
import logging
import traceback

from doula.queue.release_queue import start_release_queue
from doula.util import dumps
from doula.util import git_dirify
from doula.models.sites_dal import SiteDAL
from doula.config import Config

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
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


@view_config(route_name='environment', renderer="envs/environment.html")
def environment(request):
    env = get_env(request.matchdict['env_id'])

    return {
        'env': env, 
        'env_json': dumps(env), 
        'token': Config.get('token') 
        }

@view_config(route_name='environment_tag', renderer="string")
def environment_tag(request):
    try:
        tag_history_path = Config.get('tag_history_path')
        tag_history_remote = Config.get('tag_history_remote')
        tag = git_dirify(request.POST['tag'])
        msg = request.POST['msg']

        site = get_env(request.POST['env_id'])
        # once we have user from ldap, pass that in
        site.tag(tag_history_path, tag_history_remote, tag, msg, 'anonymous')

        return dumps({'success': True, 'env_id': site})
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

@view_config(route_name='service', renderer="services/index.html")
def service(request):
    try:
        env = get_env(request.matchdict['env_id'])
        service = env.services[request.matchdict['serv_id']]
        
    except Exception:
        msg = 'Unable to find site and service under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['env_id'], request.matchdict['serv_id'])

        raise HTTPNotFound(msg)

    return { 'env': env, 'service': service }


@view_config(route_name='service_details', renderer="services/service_details.html")
def service_details(request):
    try:
        env = get_env(request.matchdict['env_id'])
        service = env.services[request.matchdict['serv_id']]
        
    except Exception:
        msg = 'Unable to find site and service under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['env_id'], request.matchdict['serv_id'])

        raise HTTPNotFound(msg)

    return { 'env': env, 'service': service }

@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    try:
        app = SiteDAL.get_service(request.POST['env_id'], request.POST['serv_id'])
        # todo, once we have a user logged in we'll pass in the user too
        tag = git_dirify(request.POST['tag'])
        app.tag(tag, request.POST['msg'], 'anonymous')

        return dumps({'success': True, 'app': app})
    except KeyError:
        msg = 'Unable to tag site and service under "{0}" and "{1}"'
        msg = msg.format(request.POST['env_id'], request.POST['serv_id'])

        return dumps({'success': False, 'msg': msg})


@view_config(route_name='service_deploy', renderer="string")
def service_deploy(request):
    try:
        validate_token(request)

        app = SiteDAL.get_service(SiteDAL.get_master_site(), request.POST['serv_id'])
        tag = app.get_tag_by_name(request.POST['tag'])
        # todo, for now pass in the anonymous user until we start authenticating
        app.mark_as_deployed(tag, 'anonymous')

        return dumps({'success': True, 'app': app})
    except Exception as e:
        msg = 'Unable to deploy service. Error: "{0}"'
        msg = msg.format(e.message)
        log.error(msg)

        return dumps({'success': False, 'msg': msg})

def validate_token(request):
    # Validate security token
    if(request.POST['token'] != Config.get('token')):
        raise Exception("Invalid security token")

def get_env(env_name):
    env = SiteDAL.get_env(env_name)

    if not env:
        msg = 'Unable to find env "{0}"'.format(env_name)
        raise HTTPNotFound(msg)

    return env

@view_config(route_name="service_freeze")
def service_freeze(request):
    env = get_env(request.matchdict['env_id'])
    service = env.services[request.matchdict['serv_id']]

    response = Response(content_type='service/octet-stream')
    file_name = service.env_name + '_' + service.name_url + '_requirements.txt'
    response.content_disposition = 'attachment; filename="' + file_name + '"'
    response.charset = "UTF-8"
    response.text = service.freeze_requirements()

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
        msg = msg.format(request.POST['env_id'], request.POST['serv_id'])

        return dumps({'success': False, 'msg': msg})

# ERROR HANDLING
@view_config(context=HTTPNotFound, renderer='error/404.html')
def not_found(self, request):
    request.response.status = 404

    return { 'msg': request.exception.message }

@subscriber(ApplicationCreated)
def load_config(event):
    """
    Load the Application config settings
    """
    Config.load_config(event.app.registry.settings)
