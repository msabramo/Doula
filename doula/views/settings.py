from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.models.user import User
from doula.util import *
from doula.views.helpers import *
from pyramid.view import view_config


# SETTINGS VIEWS
@view_config(route_name='settings', renderer='settings/index.html')
def show_settings(request):
    sites_and_services = SiteDAL.list_of_sites_and_services()
    sites_and_services.sort()

    return {
        'config': Config,
        'user': request.user,
        'sites_and_services': sites_and_services
    }


@view_config(route_name='settings', renderer='json', request_method='POST')
def change_settings(request):
    kwargs = request.POST

    user = User.find(request.user['username'])

    for key, value in kwargs.items():
        user['settings'][key] = value

    User.save(user)

    return {'success': True}
