from doula.config import Config
from doula.util import *
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.renderers import render_to_response
import traceback
from pyramid.security import (
    NO_PERMISSION_REQUIRED
)
import logging

log = logging.getLogger('doula')

##################
# ERROR HANDLING
##################


def log_error(e, request):
    tb = traceback.format_exc()
    print "TRACEBACK\n" + str(tb)

    log_vals = {'url': request.url, 'error': e.message, 'stacktrace': tb}
    log.error(to_log_msg(log_vals))


@view_config(context=HTTPNotFound, renderer='error/404.html', permission=NO_PERMISSION_REQUIRED)
def not_found(request):
    request.response.status = 404
    log_error(request.exception, request)

    return {'msg': request.exception.message, 'config': Config}


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

    # occassionally the message is already unicode
    if not type(e.message) is unicode:
        msg = unicode(e.message, errors='replace')
    else:
        msg = e.message

    return render_to_response('doula:templates/error/exception.html',
                              {'msg': msg,
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
