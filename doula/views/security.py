import json
import requests
from velruse import login_url
from doula.cache import Cache
from pyramid.view import (
    view_config,
    forbidden_view_config
)
from pyramid.security import (
    NO_PERMISSION_REQUIRED,
    remember
)
from pyramid.httpexceptions import HTTPFound


@view_config(name='login', permission=NO_PERMISSION_REQUIRED)
@forbidden_view_config(renderer='clusterflunk:templates/login.mako')
def login_view(request):
    return HTTPFound(location=login_url(request, 'github'))


@view_config(context='velruse.AuthenticationComplete', permission=NO_PERMISSION_REQUIRED)
def login_complete_view(request):
    """
    doula:user:jayd3e
    {
        'username': '',
        'oauth_token': '',
        'avatar_url': '',
        'email': ''
    }
    """
    cache = Cache.cache()
    context = request.context
    profile = context.profile
    credentials = context.credentials

    r = requests.get('https://api.github.com/users/%s' % profile['preferredUsername'],
                     params={'auth_token': credentials['oauthAccessToken']})
    info = r.json

    user = {
        'username': profile['preferredUsername'],
        'oauth_token': credentials['oauthAccessToken'],
        'avatar_url': info['avatar_url'],
        'email': profile['emails'][0]['value']
    }
    cache.set('doula:user:%s' % user['username'], json.dumps(user))
    remember(request, user['username'])
    return  HTTPFound(location='/')


@view_config(context='velruse.AuthenticationDenied', renderer='doula:templates/error/exception.mako', permission=NO_PERMISSION_REQUIRED)
def login_denied_view(request):
    return {
        'result': 'denied',
    }
