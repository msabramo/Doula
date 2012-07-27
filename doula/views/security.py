import json
from velruse import login_url
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


@view_config(name='login', renderer='myapp:templates/login.mako', permission=NO_PERMISSION_REQUIRED)
@forbidden_view_config(renderer='clusterflunk:templates/login.mako')
def login_view(request):
    return HTTPFound(location=login_url(request, 'github'))


@view_config(context='velruse.AuthenticationComplete', renderer='myapp:templates/result.mako', permission=NO_PERMISSION_REQUIRED)
def login_complete_view(request):
    context = request.context
    result = {
        'profile': context.profile,
        'credentials': context.credentials,
    }
    return {
        'result': json.dumps(result, indent=4),
    }


@view_config(context='velruse.AuthenticationDenied', renderer='myapp:templates/result.mako', permission=NO_PERMISSION_REQUIRED)
def login_denied_view(request):
    return {
        'result': 'denied',
    }
