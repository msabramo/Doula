import json
import requests
from velruse import login_url
from doula.cache import Cache
from doula.config import Config
from pyramid.view import (
    view_config,
    forbidden_view_config
)
from pyramid.security import (
    NO_PERMISSION_REQUIRED,
    remember,
    forget
)
from pyramid.httpexceptions import HTTPFound


@view_config(name='login', permission=NO_PERMISSION_REQUIRED)
@forbidden_view_config(renderer='clusterflunk:templates/login.mako')
def login_view(request):
    return HTTPFound(location=login_url(request, 'github'))


@view_config(name='logout', permission=NO_PERMISSION_REQUIRED)
def logout_view(request):
    forget(request)
    return HTTPFound(location='/login')


@view_config(context='velruse.AuthenticationComplete', permission=NO_PERMISSION_REQUIRED)
def login_complete_view(request):
    """
    doula:user:jayd3e
    {
        'username': '',
        'oauth_token': '',
        'avatar_url': '',
        'email': '',
        'settings': {
            'notify_me': 'always'
        }
    }
    """
    cache = Cache.cache()
    context = request.context
    profile = context.profile
    credentials = context.credentials

    username = profile['preferredUsername']
    user_exists = cache.get('doula:user:%s' % username)
    if not user_exists:
        r = requests.get('https://api.github.com/users/%s' % username,
                         params={'auth_token': credentials['oauthAccessToken']})
        info = r.json

        user = {
            'username': username,
            'oauth_token': credentials['oauthAccessToken'],
            'avatar_url': info['avatar_url'],
            'email': profile['emails'][0]['value'],
            'settings': {
                'notify_me': 'always'
            }
        }
        cache.set('doula:user:%s' % user['username'], json.dumps(user))
    remember(request, username)
    return  HTTPFound(location='/')


@view_config(context='velruse.AuthenticationDenied', renderer='doula:templates/error/exception.html', permission=NO_PERMISSION_REQUIRED)
def login_denied_view(request):
    return {
        'result': 'denied',
        'config': Config
    }
