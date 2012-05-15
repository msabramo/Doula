from pyramid.config import Configurator
from pyramid.response import Response
from pyramid_jinja2 import renderer_factory
import ldap
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
import yaml
import os
import pkg_resources

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

class RootFactory(object):
    __acl__ = [(Allow, Authenticated, 'view')]
    def __init__(self, request):
        pass

def main(global_config, **settings):
    """
    Serve Doula
    """
    config = Configurator(settings=settings, root_factory=RootFactory)
    ldap_settings = {}

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../etc/ldap.yaml')) as f:
        ldap_settings = yaml.load(f)

    config.set_default_permission('view')

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(ldap_settings['auth_pw'],
                                    callback=groupfinder)
        )

    config.set_authorization_policy(
        ACLAuthorizationPolicy()
        )

    # Jinja2 config
    config.add_renderer('.html', renderer_factory)
    config.include('pyramid_jinja2')

    # ldap setup
    config.include('pyramid_ldap')

    #possibly remove the s in ldaps
    config.ldap_setup(
        'ldap://%s' % ldap_settings['ldap_ip'],
        bind = ldap_settings['setup_dn'],
        passwd = ldap_settings['ldap_pw'],
        )

    config.ldap_set_login_query(
        base_dn=ldap_settings['login_dn'],
        filter_tmpl='(sAMAccountName=%(login)s)',
        scope=ldap.SCOPE_ONELEVEL,
        )

    config.ldap_set_groups_query(
        base_dn=ldap_settings['group_dn'],
        filter_tmpl='(&(objectCategory=group)(member=%(userdn)s))',
        scope=ldap.SCOPE_SUBTREE,
        cache_period = 600,
        )

    # Scan this module
    config.scan('doula.views')
    #TODO: add this to the security/include_me function, as well as the views
    config.scan('doula.views_security')

    config.add_static_view(name='js', path='static/js')
    config.add_static_view(name='prodjs', path='static/prodjs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='images', path='static/images')

    # routes for application
    config.add_route('home', '/')
    config.add_route('sites', '/sites')
    config.add_route('site', '/sites/{site}')
    config.add_route('site_log', '/sites/{site}/logs')
    config.add_route('application', '/sites/{site}/{application}')
    config.add_route('app_requirements_file', '/sites/{site}/{application}/freeze')
    config.add_route('register', '/register')
    config.add_route('deploy', '/deploy')
    config.add_route('tag', '/tag')
    config.add_route('nodes_ip_lookup', '/nodes/ip_addresses')

    config.add_route('login', '/login')
    config.add_route('forbidden', '/forbidden')
    config.add_route('logout', '/logout')

    return config.make_wsgi_app()
