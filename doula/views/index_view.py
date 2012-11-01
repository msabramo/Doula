# from doula.views.view_helpers import *
from doula.cache import Redis
from doula.config import Config
from doula.jobs_timer import start_task_scheduling
from doula.models.doula_dal import DoulaDAL
from doula.queue import Queue
from doula.util import dumps
from doula.util import git_dirify
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
import logging
import os
import simplejson as json

log = logging.getLogger(__name__)


# SITE VIEWS
@view_config(route_name='home', renderer='sites/index.html')
def show_home(request):
    return show_sites(request)


@view_config(route_name='sites', renderer='sites/index.html')
def show_sites(request):
    """
    Show the testing sites
    """
    dd = DoulaDAL()
    sites = dd.get_all_sites()

    return {
        'config': Config,
        'sites': sites,
        'sites_count': len(sites.keys()),
        'username': request.user['username']
    }


@view_config(route_name='site', renderer="sites/site.html")
def site(request):
    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])

    return {
        'site': site,
        'user': request.user,
        'site_json': dumps(site),
        'token': Config.get('token'),
        'config': Config
    }


@view_config(route_name='site_lock', renderer="json")
def site_lock(request):
    # Ensure the user is an admin before taking any action
    if not request.user['admin']:
        return {'success': False, 'msg': 'You must be a Doula Admin to lock down a site.'}

    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])

    if request.POST['lock'] == 'true':
        site.lock()
    else:
        site.unlock()

    return {'success': True}


@view_config(route_name='site_tag', renderer="string")
def site_tag(request):
    tag_history_path = Config.get('tag_history_path')
    tag_history_remote = Config.get('tag_history_remote')
    tag = git_dirify(request.POST['tag'])
    msg = request.POST['msg']

    dd = DoulaDAL()
    site = dd.find_site_by_name(request.matchdict['site_name'])
    site.tag(tag_history_path, tag_history_remote, tag, msg, 'anonymous')

    return dumps({'success': True, 'site_name': site})


# BAMBINO VIEWS
@view_config(route_name='bambino_register', renderer='json', permission=NO_PERMISSION_REQUIRED)
def bambino_register(request):
    """
    Register a Bambino node with Doula.
    """
    node = json.loads(request.POST['node'])
    dd = DoulaDAL()

    if(request.POST['action'] == 'register'):
        dd.register_node(node)
    else:
        dd.unregister_node(node)

    return {'success': 'true'}


@view_config(route_name='bambino_ips', renderer="string", permission=NO_PERMISSION_REQUIRED)
def bambino_ips(request):
    """
    Return all the IP addresses for the Bambinos.
    Used for deployment to update every Bambino registered with Doula.
    """
    dd = DoulaDAL()
    return json.dumps({
        'success': True,
        'ip_addresses': dd.get_all_bambino_ips()
    })


@view_config(route_name='updatedoula', renderer="updatedoula.html")
def updatedoula(request):
    """
    Update Doula makes calls to update all the data Doula depends on
    e.g.
    """
    q = Queue()

    html = ''
    jobs = [
        'cleanup_queue',
        'pull_github_data',
        'pull_appenv_github_data',
        'pull_cheeseprism_data',
        'pull_bambino_data']

    for job in jobs:
        q.this({'job_type': job})
        html += job + ', '

    return {'jobs_html': html.rstrip(', ')}


@view_config(route_name='docs', permission=NO_PERMISSION_REQUIRED)
def docs_view(request):
    return HTTPFound(location='http://code.corp.surveymonkey.com/pages/DevOps/DoulaDocs/docs/')


####################
# Service events
####################

@subscriber(ApplicationCreated)
def load_config(event):
    """
    Load the Service config settings
    """
    Config.load_config(event.app.registry.settings)
    Redis.get_instance().set('doula:settings', dumps(event.app.registry.settings))

    # When the service starts we'll make sure Doula updates it self pulling
    updatedoula(None)

    start_task_scheduling()


@view_config(route_name='favicon')
def favicon_view(request):
    here = os.path.dirname(__file__).replace('views', '')
    icon = os.path.join(here, 'static', 'favicon.ico')
    return FileResponse(icon, request=request)
