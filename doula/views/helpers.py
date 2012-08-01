from doula.config import Config
from doula.models.sites_dal import SiteDAL
from doula.util import *
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.renderers import render_to_response
import traceback

import logging

log = logging.getLogger('doula')


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
    log_error(request.exception, request)

    return {'msg': request.exception.message, 'config': Config}


def log_error(e, request):
    tb = traceback.format_exc()
    print "TRACEBACK\n" + str(tb)

    log_vals = {'url': request.url, 'error': e.message, 'stacktrace': tb}
    log.error(to_log_msg(log_vals))


def handle_json_exception(e, request):
    request.response.status = 500
    log_error(e, request)
    tb = traceback.format_exc()

    return render_to_response('string',
                              dumps({'success': False, 'msg': e.message, 'stacktrace': tb}))


def handle_exception(e, request):
    request.response.status = 500
    request.override_renderer = 'error/exception.html'
    log_error(e, request)
    tb = traceback.format_exc()

    return render_to_response('doula:templates/error/exception.html',
                              {'msg': unicode(e.message, errors='replace'),
                               'stacktrace': unicode(tb, errors='replace'),
                               'config': Config, 'request': request})


def exception_tween_factory(handler, registry):
    def exception_tween(request):
        try:
            response = handler(request)
            return response
        except Exception as e:
            if request.is_xhr is True:
                return handle_json_exception(e, request)
            return handle_exception(e, request)
    return exception_tween
