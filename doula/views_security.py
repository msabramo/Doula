from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
import ldap

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.httpexceptions import HTTPFound

from pyramid.security import (
   Allow,
   Authenticated,
   remember,
   forget,
   )

from pyramid_ldap import (
    get_ldap_connector,
    groupfinder,
    )

@view_config(route_name='login', renderer='login.html')
@forbidden_view_config(renderer='login.html')
def login(request):
    url = request.current_route_url()
    login = ''
    password = ''
    error = ''

    if 'form.submitted' in request.POST:
        login = request.POST['login']
        password = request.POST['password']
        connector = get_ldap_connector(request)
        data = connector.authenticate(login, password)
        if data is not None:
            dn = data[0]
            headers = remember(request, dn)
            return HTTPFound('/', headers=headers)
        else:
            error = 'Invalid credentials'

    return dict(
        login_url=url,
        login=login,
        password=password,
        error=error,
        )

@view_config(route_name='forbidden', permission='view')
def logged_in(request):
    return {'i am forbidden!':'yes'}
