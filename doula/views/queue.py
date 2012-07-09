from doula.config import Config
from doula.views.helpers import *
from pyramid.view import view_config


# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    return {'config': Config}
