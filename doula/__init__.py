# import os
# import yaml
# import ldap
from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
# from pyramid.authentication import AuthTktAuthenticationPolicy
# from pyramid.authorization import ACLAuthorizationPolicy
# from pyramid_ldap import groupfinder


def main(global_config, **settings):
    """
    Serve Doula.
    """
    config = Configurator(settings=settings)

    # ldap_settings = {}
    # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../etc/ldap.yaml')) as f:
    #     ldap_settings = yaml.load(f)

    # config.set_default_permission('view')

    # config.set_authentication_policy(
    #     AuthTktAuthenticationPolicy(ldap_settings['auth_pw'],
    #                                 callback=groupfinder)
    #     )

    # config.set_authorization_policy(
    #     ACLAuthorizationPolicy()
    #     )

    # # ldap setup
    # config.include('pyramid_ldap')

    # #possibly remove the s in ldaps
    # config.ldap_setup(
    #     'ldap://%s' % ldap_settings['ldap_ip'],
    #     bind=ldap_settings['setup_dn'],
    #     passwd=ldap_settings['ldap_pw'],
    #     )

    # config.ldap_set_login_query(
    #     base_dn=ldap_settings['login_dn'],
    #     filter_tmpl='(sAMAccountName=%(login)s)',
    #     scope=ldap.SCOPE_ONELEVEL,
    #     )

    # config.ldap_set_groups_query(
    #     base_dn=ldap_settings['group_dn'],
    #     filter_tmpl='(&(objectCategory=group)(member=%(userdn)s))',
    #     scope=ldap.SCOPE_SUBTREE,
    #     cache_period=600,
    #     )

    # Tweens
    config.add_tween('doula.views.helpers.exception_tween_factory')

    # Jinja2 config
    config.add_renderer('.html', renderer_factory)
    config.include('pyramid_jinja2')

    config.add_static_view(name='js', path='static/js')
    config.add_static_view(name='prodjs', path='static/prodjs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='images', path='static/images')
    config.add_static_view(name='img', path='static/img')

    # routes for doula
    config.add_route('favicon', '/favicon.ico')
    config.add_route('home', '/')
    config.add_route('sites', '/sites')

    config.add_route('site', '/sites/{site_id}')
    config.add_route('site_tag', '/sites/{site_id}/tag')

    config.add_route('service', '/sites/{site_id}/{serv_id}')
    config.add_route('service_tag', '/sites/{site_id}/{serv_id}/tag')
    config.add_route('service_freeze', '/sites/{site_id}/{serv_id}/freeze')
    config.add_route('service_deploy', '/sites/{site_id}/{serv_id}/deploy')
    config.add_route('service_details', '/sites/{site_id}/{serv_id}/details')
    config.add_route('service_cheese_prism_modal', '/sites/{site_id}/{serv_id}/cheese_prism_modal')
    config.add_route('service_cheese_prism_push', '/sites/{site_id}/{serv_id}/cheese_prism_push')

    config.add_route('queue', '/queue')
    config.add_route('settings', '/settings')

    config.add_route('bambino_register', '/bambino/register')
    config.add_route('bambino_ips', '/bambino/ip_addresses')

    config.add_route('login', '/login')
    config.add_route('forbidden', '/forbidden')
    config.add_route('logout', '/logout')

    # Scan this module
    config.scan('doula.views')
    return config.make_wsgi_app()
