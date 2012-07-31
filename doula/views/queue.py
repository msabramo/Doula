import os.path
import time
from datetime import datetime

from doula.config import Config
from doula.views.helpers import *
from doula.queue import Queue
from pyramid.view import view_config
from pyramid.renderers import render
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter


def get_log(job_id):
    log = ''
    log_name = os.path.join('/var/log/doula', job_id + '.log')
    with open(log_name) as log_file:
        log = log_file.read()

    return highlight(log, BashLexer(), HtmlFormatter())


# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    queue = Queue()

    query = {'job_type': ['push_to_cheeseprism', 'cycle_services']}
    sort_by = request.params.get('sort_by')
    if sort_by == 'complete' or sort_by == 'failed' or sort_by == 'queued':
        query['status'] = sort_by
    last_updated = datetime.now()
    queued_items = queue.get(query)

    i = 0
    for queued_item in queued_items:
        queued_items[i]['log'] = ''
        # If job is already completed/failed
        if queued_item['status'] in ['complete', 'failed']:
            queued_items[i]['log'] = get_log(queued_item['id'])
        i += 1

    # sort all of the items with respect to time
    queued_items = sorted(queued_items, key=lambda k: k['time_started'])
    # descending order
    queued_items = reversed(queued_items)

    last_updated = time.mktime(last_updated.timetuple())

    return {'config': Config,
            'queued_items': queued_items,
            'last_updated': last_updated}


@view_config(route_name='queue', request_param='last_updated', renderer='json', xhr=True)
def update_queue(request):
    queue = Queue()
    last_updated = request.GET['last_updated']

    query = {'job_type': ['push_to_cheeseprism', 'cycle_services']}
    queued_items = queue.get(query)

    i = 0
    new_queued_items = []
    for queued_item in queued_items:
        queued_item = queued_items[i]

        # If job is already completed/failed
        if queued_item['status'] in ['complete', 'failed']:
            queued_item['log'] = get_log(queued_item['id'])

        # If the job has not been displayed on the interface yet
        if queued_item['time_started'] > int(last_updated):
            queued_item['html'] = render('doula:templates/queue/queued_item.html',
                                         {'queued_item': queued_item})
            new_queued_items.append(queued_item)
        i += 1

    # sort all of the items with respect to time
    new_queued_items = sorted(new_queued_items, key=lambda k: k['time_started'])

    return {'success': True,
            'queued_items': queued_items,
            'new_queued_items': new_queued_items}
