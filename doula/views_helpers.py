from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.util import *
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
import traceback


def get_site(site_name):
    site = SiteDAL.get_site(site_name)

    if not site:
        msg = 'Unable to find site "{0}"'.format(site_name)
        raise HTTPNotFound(msg)

    return site

##################
# ERROR HANDLING
##################


@view_config(context=HTTPNotFound, renderer='error/404.html')
def not_found(self, request):
    request.response.status = 404
    log_error(request.exception, request.exception.message, request)

    return {'msg': request.exception.message, 'config': Config}


def handle_json_exception(e, msg, request):
    request.response.status = 500
    log_error(e, msg, request)
    tb = traceback.format_exc()

    return dumps({'success': False, 'msg': msg, 'stacktrace': tb})


def handle_exception(e, request):
    request.response.status = 500
    request.override_renderer = 'error/exception.html'
    log_error(e, e.message, request)
    tb = traceback.format_exc()

    return {'msg': e.message, 'stacktrace': tb, 'config': Config}


def log_error(e, msg, request):
    tb = traceback.format_exc()
    print "TRACEBACK\n" + str(tb)

    log_vals = {'url': request.url, 'error': msg, 'stacktrace': tb}
    log.error(to_log_msg(log_vals))
