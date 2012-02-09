from doula.resources import App
from pyramid.view import view_config

import os
import json

def includeme(config):
    config.scan(__name__)
    config.add_route('show_doula', '/doula/', factory=App.root_factory)

@view_config(route_name="show_doula", renderer='doula_home.html', context=App)
def show_doula(context, request):
    # make call to backend here
    applications = get_applications()
    is_ready_for_release = get_is_ready_for_release(applications)
    
    return { 'applications' : applications, 'is_ready_for_release' : is_ready_for_release }
	
def get_is_ready_for_release(applications):
    for application in applications:
        if application['status'] == 'uncommitted_changes':
            return False
    
    return True

def get_applications():
    data = open(os.getcwd() + '/data.json')
    json_data = data.read()
    data.close()
    
    return json.loads(json_data)