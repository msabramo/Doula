from doula.resources import App
from pyramid.view import view_config
from pyramid.renderers import render

import os
import json

def includeme(config):
    config.scan(__name__)
    config.add_route('show_sites', '/', factory=App.root_factory)
    config.add_route('show_site_status', '/sites/{url}/', factory=App.root_factory)
    config.add_route('revert_app', '/sites/app/revert/', factory=App.root_factory)

@view_config(route_name="show_sites", renderer="sites.html", context=App)
def show_sites(context, request):
    sites = get_sites()
    
    return { 'sites': sites }

def get_sites():
    return get_json_from_file('sites.json')

@view_config(route_name="show_site_status", renderer='site.html', context=App)
def show_site_status(context, request):
    sites = get_sites()
    selected_site = [site for site in sites if site['url'] == request.matchdict['url']][0]
    
    applications = get_applications()
    is_ready_for_release = get_is_ready_for_release(applications)
    
    return { 
        'sites': sites,
        'site': selected_site,
        'applications' : applications, 
        'is_ready_for_release' : is_ready_for_release 
    }

@view_config(route_name="revert_app", renderer='json', context=App)
def revert_app(context, request):
    app = get_app_by_id(request.POST['id'])
    app = revert_app_status(app)
    html = get_app_html(app)
    
    return { 'app': json.dumps(app), 'html': html }

# Helper functions
def revert_app_status(app):
    app['status'] = 'unchanged'
    
    return app

def get_app_by_id(id):
    applications = get_applications()
    apps = [app for app in applications if app['id'] == int(id)]
    
    return apps[0]

def get_app_html(app):
    tpl = 'templates/application_row.html'
    
    return render(tpl, { 'application': app })

def get_is_ready_for_release(applications):
    for application in applications:
        if application['status'] == 'uncommitted_changes':
            return False
    
    return True

def get_applications():
    applications = get_json_from_file('applications.json')
    id_counter = 1
    
    # apply ids
    for app in applications:
        app['id'] = id_counter
        id_counter +=1
    
    return applications

def get_json_from_file(file_name):
    data = open(os.getcwd() + '/dummy_data/' + file_name)
    json_data = data.read()
    data.close()
    
    return json.loads(json_data)
