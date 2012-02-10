from doula.request import Request
from bambino.resources import App
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid_jinja2 import renderer_factory
from doula import plugin


def main(global_config, **settings):
    this = 'Doula'
    settings = dict(settings)
    settings.setdefault('jinja2.i18n.domain', this)
    session_factory = UnencryptedCookieSessionFactoryConfig(this)
    plugins = list(plugin.specs_from_str(settings['doula.plugins']))
    app = App.factory(plugins, settings)
    config = Configurator(root_factory=app.root_factory,
                          settings=settings, session_factory=session_factory)
    config.set_request_factory(Request)
    config.add_translation_dirs('locale/')
    config.include('pyramid_jinja2')
    config.scan('doula.views')
    config.add_renderer('.html', renderer_factory)
    
    # Routing for static files
    config.add_static_view(name='js', path='static/js')
    config.add_static_view(name='prodjs', path='static/prodjs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='images', path='static/images')
    config.add_static_view('static', 'static')

    [config.include(plug) for plug in plugins if plug]
        
    return config.make_wsgi_app()

