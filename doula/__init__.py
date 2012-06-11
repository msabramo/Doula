from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory


def main(global_config, **settings):
    """
    Serve Doula.
    """
    config = Configurator(settings=settings)

    # Jinja2 config
    config.add_renderer('.html', renderer_factory)
    config.include('pyramid_jinja2')

    # Scan this module
    config.scan('doula.views')

    config.add_static_view(name='js', path='static/js')
    config.add_static_view(name='prodjs', path='static/prodjs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='images', path='static/images')

    config.add_static_view(name='wf', path='templates/wireframes/static')

    # routes for application
    config.add_route('home', '/')
    config.add_route('sites', '/sites')
    config.add_route('site', '/sites/{site}')
    config.add_route('site_log', '/sites/{site}/logs')
    config.add_route('application', '/sites/{site}/{application}')
    config.add_route('app_requirements_file', '/sites/{site}/{application}/freeze')
    config.add_route('register', '/register')
    config.add_route('deploy_old', '/deploy')
    config.add_route('tag_site', '/tagsite')
    config.add_route('tag', '/tag')
    config.add_route('nodes_ip_lookup', '/nodes/ip_addresses')

    config.add_route('wfhome', '/wfhome')
    config.add_route('appenvs', '/appenvs')
    config.add_route('deploy', '/deploy')
    config.add_route('packages', '/packages')
    config.add_route('queue', '/queue')
    config.add_route('settings', '/settings')

    return config.make_wsgi_app()
