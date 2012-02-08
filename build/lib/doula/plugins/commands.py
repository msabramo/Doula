from doula.resources import App
from pyramid.view import view_config
from path import path
import subprocess

def includeme(config):
    config.scan(__name__)
    config.add_route('memory', 'memory/{pid}', factory=App.root_factory)

@view_config(route_name='memory', renderer='json')
def memory(context, request, ps='ps -orss= -p %d'):
    pid = request.matchdict.get('pid', None)
    if not pid:
        pid = context.pid
    pid = int(pid)
    mem = subprocess.check_output((ps % pid).split())
    return {'mem':mem}


@view_config(name='logdump', context=App, renderer='json')
def syslog_dump(context, request):
    outfile = path(request.settings['doula.plugins.commands.outfile'])
    with open(outfile, 'w'):
        ## you'd want to capture this with a try or a context manager
        ## if the command raises a nonzero exit status, so will check_call
        ret = subprocess.check_call('syslog >> %s' %outfile, shell=True)
    return dict(ret=ret)
