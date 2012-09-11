from doula.models.user import User
from doula.resources import Site
from doula.security import groupfinder
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid_jinja2 import renderer_factory


def main(global_config, **settings):
    """
    Serve Doula.
    """
    authentication_policy = SessionAuthenticationPolicy(callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()
    session_factory = UnencryptedCookieSessionFactoryConfig(settings['doula.session.secret'],
                                                            cookie_max_age=2592000)
    config = Configurator(settings=settings,
                          root_factory=Site,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          session_factory=session_factory)

    # Github integration
    config.include('velruse.providers.github')
    config.add_github_login_from_settings(prefix='github.')

    # Security
    config.set_default_permission('authenticated')

    # Tweens
    config.add_tween('doula.views.helpers.exception_tween_factory')

    # Request
    config.set_request_property(User.find_user_for_request, 'user', reify=True)

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
    config.add_route('docs', '/docs')
    config.add_route('sites', '/sites')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('updatedoula', '/updatedoula')

    config.add_route('site', '/sites/{site_id}')
    config.add_route('site_tag', '/sites/{site_id}/tag')

    config.add_route('service', '/sites/{site_id}/{serv_id}')
    config.add_route('service_tag', '/sites/{site_id}/{serv_id}/tag')
    config.add_route('service_cycle', '/sites/{site_id}/{serv_id}/cycle')
    config.add_route('service_freeze', '/sites/{site_id}/{serv_id}/freeze')
    config.add_route('service_deploy', '/sites/{site_id}/{serv_id}/deploy')
    config.add_route('service_release', '/sites/{site_id}/{serv_id}/release')
    config.add_route('service_details', '/sites/{site_id}/{serv_id}/details')
    config.add_route('service_cheese_prism_modal', '/sites/{site_id}/{serv_id}/cheese_prism_modal')
    config.add_route('service_cheese_prism_push', '/sites/{site_id}/{serv_id}/cheese_prism_push')

    config.add_route('queue', '/queue')
    config.add_route('settings', '/settings')

    config.add_route('bambino_register', '/bambino/register')
    config.add_route('bambino_ips', '/bambino/ip_addresses')

    # Scan this module
    config.scan('doula.views')

    return config.make_wsgi_app()
