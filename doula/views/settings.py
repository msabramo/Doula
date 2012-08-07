import json

from doula.config import Config
from doula.util import *
from doula.cache import Cache
from doula.views.helpers import *
from pyramid.view import view_config


# SETTINGS VIEWS
@view_config(route_name='settings', renderer='settings/index.html')
def show_settings(request):
    return {'config': Config}


@view_config(route_name='settings', renderer='json', request_method='POST')
def change_settings(request):
    kwargs = request.POST

    cache = Cache.cache()
    user = cache.get('doula:user:%s' % request.user['username'])
    user = json.loads(user)
    for key, value in kwargs.items():
        user['settings'][key] = value
    cache.set('doula:user:%s' % request.user['username'], json.dumps(user))
    return {'success': 1}
