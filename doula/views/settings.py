from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.models.user import User
from doula.util import *
from doula.views.helpers import *
from pyramid.view import view_config


# SETTINGS VIEWS
@view_config(route_name='settings', renderer='settings/index.html')
def show_settings(request):
    return {
        'config': Config,
        'user': request.user,
        'sas': SiteDAL.list_of_sites_and_services()
    }


@view_config(route_name='settings', renderer='json', request_method='POST')
def change_settings(request):
    kwargs = request.POST

    user = User.find(request.user['username'])

    for key, value in kwargs.items():
        if key == 'notify_me':
            user['settings']['notify_me'] = value
        elif key == 'subscribed_to':
            subscription_list = value.split(',')
            subscription_list.append('my_jobs')
            user['settings']['subscribed_to'] = subscription_list

    User.save(user)

    return {'success': True}
