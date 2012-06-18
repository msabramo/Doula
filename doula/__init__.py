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
    config.add_static_view(name='img', path='static/img')

    # routes for doula
    config.add_route('home', '/')
    config.add_route('envs', '/envs')
    
    config.add_route('environment', '/envs/{env_id}')
    config.add_route('environment_tag', '/envs/{env_id}/tag')

    config.add_route('service', '/envs/{env_id}/{serv_id}')
    config.add_route('service_tag', '/envs/{env_id}/{serv_id}/tag')
    config.add_route('service_freeze', '/envs/{env_id}/{serv_id}/freeze')
    config.add_route('service_deploy', '/envs/{env_id}/{serv_id}/deploy')
    config.add_route('service_details', '/envs/{env_id}/{serv_id}/details')

    config.add_route('queue', '/queue')
    config.add_route('settings', '/settings')

    config.add_route('bambino_register', '/bambino/register')
    config.add_route('bambino_ips', '/bambino/ip_addresses')

    return config.make_wsgi_app()
