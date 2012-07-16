import os.path

from doula.config import Config
from doula.views.helpers import *
from doula.queue import Queue
from pyramid.view import view_config
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter


# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    queue = Queue()

    query = {}
    sort_by = request.params.get('sort_by')
    if sort_by == 'complete' or sort_by == 'failed' or sort_by == 'queued':
        query = {'status': sort_by}
    queued_items = queue.get(query)

    i = 0
    for queued_item in queued_items:
        log = ''

        # If job is already completed/failed
        if queued_item['status'] in ['complete', 'failed']:
            log_name = os.path.join('/var/log/doula', queued_item['id'] + '.log')
            with open(log_name) as log_file:
                log = log_file.read()

        queued_items[i]['log'] = highlight(log, BashLexer(), HtmlFormatter())
        i += 1

    # sort all of the items with respect to time
    queued_items = sorted(queued_items, key=lambda k: k['time_started'])
    # descending order
    queued_items = reversed(queued_items)
    return {'config': Config,
            'queued_items': queued_items}


@view_config(route_name='queue', renderer='json', xhr=True)
def update_queue(request):
    return {}
