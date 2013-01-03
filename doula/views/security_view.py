from doula.models.user import User
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
from velruse import login_url
import requests


@view_config(name='login', permission=NO_PERMISSION_REQUIRED)
@forbidden_view_config()
def login_view(request):
    return HTTPFound(location=login_url(request, 'github'))


@view_config(route_name='logout', permission=NO_PERMISSION_REQUIRED)
def logout_view(request):
    forget(request)
    return HTTPFound(location='http://code.corp.surveymonkey.com')


@view_config(context='velruse.AuthenticationComplete', permission=NO_PERMISSION_REQUIRED)
def login_complete_view(request):
    """
    Log the user in and update their user values.
    If the user doesn't exist create the user

    Example user dict:
        doula:user:jayd3e
        {
            'username': '',
            'oauth_token': '',
            'avatar_url': '',
            'email': '',
            'settings': {
                'notify_me': 'always',
                'subscribed_to': ['my_jobs']
            }
        }
    """
    profile = request.context.profile
    credentials = request.context.credentials
    username = profile['preferredUsername']

    # r = requests.get('https://api.github.com/users/%s' % username,
    #                  params={'auth_token': credentials['oauthAccessToken']})

    # import pdb; pdb.set_trace()
    # github_user_info = r.json

    user = User.find(username)

    # If a user exists we still pull the latest users avatar url and email
    # because those are updated by the user in Github Enterprise.
    if user:
        user['avatar_url'] = ''
        user['email'] = get_email_from_profile(profile)
        user['oauth_token'] = credentials['oauthAccessToken']
    else:
        user = {
            'username': username,
            'oauth_token': credentials['oauthAccessToken'],
            'avatar_url': '',
            'email': get_email_from_profile(profile),
            'settings': {
                'notify_me': 'failed',
                'subscribed_to': ['my_jobs']
            }
        }

    User.save(user)
    remember(request, username)

    return HTTPFound(location='/')


def get_email_from_profile(profile):
    """
    Find the email address. It may not be there, so we wrap the check
    """
    try:
        return profile['emails'][0]['value']
    except:
        return 'no-reply@surveymonkey.com'


@view_config(context='velruse.AuthenticationDenied', permission=NO_PERMISSION_REQUIRED)
def login_denied_view(request):
    return HTTPFound(location='/login')
