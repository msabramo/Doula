# from pyramid.view import (
#     view_config,
#     forbidden_view_config
# )
# from pyramid.response import Response
# from pyramid.httpexceptions import HTTPFound
# from pyramid_ldap import get_ldap_connector
# from pyramid.security import (
#    remember,
#    forget
# )


# @view_config(route_name='login', renderer='doula:templates/security/login.html')
# @forbidden_view_config(renderer='doula:templates/security/login.html')
# def login(request):
#     url = request.current_route_url()
#     login = ''
#     password = ''
#     error = ''

#     if 'form.submitted' in request.POST:
#         login = request.POST['login']
#         password = request.POST['password']
#         connector = get_ldap_connector(request)
#         data = connector.authenticate(login, password)
#         if data is not None:
#             dn = data[0]
#             headers = remember(request, dn)
#             return HTTPFound('/', headers=headers)
#         else:
#             error = 'Invalid credentials'

#     return dict(
#         login_url=url,
#         login=login,
#         password=password,
#         error=error,
#         )


# @view_config(route_name='logout')
# def logout(request):
#     headers = forget(request)
#     return Response('Logged out', headers=headers)
