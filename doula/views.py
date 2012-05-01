import json
import time

from doula.util import pprint
from doula.util import dumps
from doula.models.sites_dao import SiteDAO
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound


@view_config(route_name='home', renderer='home.html')
def show_home(request):
    return show_sites(request)

@view_config(route_name='sites', renderer='home.html')
def show_sites(request):
    dao = SiteDAO()
    
    return { 'sites': dao.get_sites() }

@view_config(route_name='site', renderer="site.html")
def show_site(request):
    dao = SiteDAO()
    site = dao.get_site(request.matchdict['site'])
    token = request.registry.settings['token']
    
    if not site:
        msg = 'Unable to find site "{0}"'.format(request.matchdict['site'])
        raise HTTPNotFound(msg)

    return { 'site': site, 'site_json': dumps(site), 'token': token }


@view_config(route_name='application', renderer="application.html")
def show_application(request):
    try:
        dao = SiteDAO()
        site = dao.get_site(request.matchdict['site'])
        app = site.applications[request.matchdict['application']]
        
    except Exception as e:
        msg = 'Unable to find site and application under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['site'], request.matchdict['application'])

        raise HTTPNotFound(msg)
    
    return { 'site': site, 'app': app }

@view_config(route_name='tag', renderer="string")
def tag_application(request):
    try:
        app = SiteDAO.get_application(request.POST['site'], request.POST['application'])
        app.tag(request.POST['tag'], request.POST['msg'])
        
        return dumps({ 'success': True, 'app': app })
    except KeyError as e:
        msg = 'Unable to tag site and application under "{0}" and "{1}"'
        msg = msg.format(request.POST['site'], request.POST['application'])
        
        return dumps({ 'success': False, 'msg': msg })
    

@view_config(route_name='deploy', renderer="string")
def deploy_application(request):
    try:
        # validate the security token
        if(request.POST['token'] != request.registry.settings['token']):
            raise Exception("Invalid security token")
        
        app = SiteDAO.get_application(request.POST['site'], request.POST['application'])
        app.mark_as_deployed()
        
        return dumps({ 'success': True, 'app': app })
    except Exception as e:
        msg = 'Unable to deploy application. Error: "{0}"'
        msg = msg.format(e.message)
        
        return dumps({ 'success': False, 'msg': msg })
    
@view_config(context=HTTPNotFound, renderer='404.html')
def not_found(self, request):
    request.response.status = 404
    
    return { 'msg': request.exception.message }


@view_config(route_name='nodes_ip_lookup', renderer="json")
def nodes_ip_lookup(request):
    try:
        ips = SiteDAO.get_node_ips()
        return { 'success': True, 'ip_addresses': ips }
    except KeyError as e:
        msg = 'Unable to find Bambino IP addresses "{0}"'
        msg = msg.format(request.POST['site'], request.POST['application'])
        
        return dumps({ 'success': False, 'msg': msg })

@view_config(route_name="app_requirements_file")
def app_requirements_file(request):
    dao = SiteDAO()
    site = dao.get_site(request.matchdict['site'])
    app = site.applications[request.matchdict['application']]
    
    response = Response(content_type='application/octet-stream')
    file_name = app.site_name + '_' + app.name_url + '_requirements.txt'
    response.content_disposition = 'attachment; filename="' + file_name + '"'
    response.charset = "UTF-8"
    response.text = app.freeze_requirements()
    
    return response
    

@view_config(route_name='register', renderer='json')
def register(request):
    """
    Register a Bambino node with Doula.
    """
    node = json.loads(request.POST['node'])
    node['time'] = time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime())
    
    if(request.POST['action'] == 'register'):
        SiteDAO().register_node(node)
    else:
        SiteDAO().unregister_node(node)
    
    return {'success': 'true'}

