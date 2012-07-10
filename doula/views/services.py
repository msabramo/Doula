from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.services.cheese_prism import CheesePrism
from doula.util import *
from doula.views.helpers import *
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
import logging

log = logging.getLogger(__name__)

###############
# SERVICE VIEWS
###############


@view_config(route_name='service', renderer="services/release_actions.html")
def service(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]
        other_packages = CheesePrism.other_packages(service.packages)
    except Exception:
        msg = 'Unable to find site and service under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['site_id'], request.matchdict['serv_id'])

        raise HTTPNotFound(msg)

    return {
        'site': site,
        'service': service,
        'config': Config,
        'service_json': dumps(service),
        'other_packages': other_packages
    }


@view_config(route_name='service_cheese_prism_modal', renderer="services/modal_push_to_cheese_prism.html")
def service_cheese_prism_modal(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]
        package = service.get_package_by_name(request.GET['name'])

        versions = package.get_versions()
        versions.sort()
        versions.reverse()
        current_version = versions[0]
    except Exception as e:
        msg = 'Error pulling Push New Package Modal'
        return handle_json_exception(e, msg, request)

    return {
        'service': service,
        'package': package,
        'current_version': current_version,
        'next_version': next_version(current_version)
    }

@view_config(route_name='service_details', renderer="services/service_details.html")
def service_details(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]

    except Exception:
        msg = 'Unable to find site and service under "{0}" and "{1}"'
        msg = msg.format(request.matchdict['site_id'], request.matchdict['serv_id'])

        raise HTTPNotFound(msg)

    return {'site': site, 'service': service, 'config': Config}


@view_config(route_name='service_tag', renderer="string")
def service_tag(request):
    try:
        service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])
        # todo, once we have a user logged in we'll pass in the user too
        tag = git_dirify(request.POST['tag'])
        service.tag(tag, request.POST['msg'], 'anonymous')

        # pull the updated service
        updated_service = SiteDAL.get_service(request.matchdict['site_id'], request.matchdict['serv_id'])

        return dumps({'success': True, 'service': updated_service})
    except Exception as e:
        msg = 'Unable to tag site and service under "{0}" and "{1}"'
        msg = msg.format(request.POST['site_id'], request.POST['serv_id'])
        return handle_json_exception(e, msg, request)


@view_config(route_name='service_deploy', renderer="string")
def service_deploy(request):
    try:
        validate_token(request)

        service = SiteDAL.get_service(SiteDAL.get_master_site(), request.POST['serv_id'])
        tag = service.get_tag_by_name(request.POST['tag'])
        # todo, for now pass in the anonymous user until we start authenticating
        service.mark_as_deployed(tag, 'anonymous')

        return dumps({'success': True, 'service': service})
    except Exception as e:
        msg = 'Unable to deploy service. Error: "{0}"'
        msg = msg.format(e.message)
        return handle_json_exception(e, msg, request)


def validate_token(request):
    # Validate security token
    if(request.POST['token'] != Config.get('token')):
        raise Exception("Invalid security token")


@view_config(route_name="service_freeze")
def service_freeze(request):
    try:
        site = get_site(request.matchdict['site_id'])
        service = site.services[request.matchdict['serv_id']]

        response = Response(content_type='service/octet-stream')
        file_name = service.site_name + '_' + service.name_url + '_requirements.txt'
        response.content_disposition = 'attachment; filename="' + file_name + '"'
        response.charset = "UTF-8"
        response.text = service.freeze_requirements()
    except Exception as e:
        return handle_exception(e, request)

    return response
