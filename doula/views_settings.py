from doula.config import Config
from doula.util import *
from doula.views_helpers import *
from pyramid.view import view_config


# SETTINGS VIEWS
@view_config(route_name='settings', renderer='settings/index.html')
def show_settings(request):
    return {'config': Config}
