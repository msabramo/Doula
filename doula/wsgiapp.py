import prism


def main(global_config, **settings):
    this = 'Doula'
    with prism.configurator(appname=this,
                            global_config=global_config,
                            settings=settings) as config:
        config.add_translation_dirs('locale/')
        config.scan('doula.views')

        # Routing for static files
        config.add_static_view(name='js', path='static/js')
        config.add_static_view(name='prodjs', path='static/prodjs')
        config.add_static_view(name='css', path='static/css')
        config.add_static_view(name='images', path='static/images')
        config.add_static_view('static', 'static')
        
    return config.wsgiapp



