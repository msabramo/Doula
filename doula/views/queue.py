from datetime import datetime
from doula.config import Config
from doula.log import get_log
from doula.queue import Queue
from doula.views.helpers import *
from pyramid.renderers import render
from pyramid.view import view_config
import time


# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    queue = Queue()

    query = {'job_type': ['push_to_cheeseprism', 'cycle_services', 'push_service_environment']}
    sort_by = request.params.get('sort_by')
    if sort_by == 'complete' or sort_by == 'failed' or sort_by == 'queued':
        query['status'] = sort_by

    # Filter by filters by username, or all users
    filter_by = request.params.get('filter_by')

    if filter_by == 'myjobs' or not filter_by:
        query['user_id'] = request.user['username']

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


def pull_queued_items(request):
    """

    """
    # alextodo. what does this actually return timewise?
    # can we look for stuff in the last 10 minutes?
    filter_by = request.GET['filter_by']

    query = {
        'job_type': [
            'push_to_cheeseprism',
            'cycle_services',
            'push_service_environment']
        }

    if filter_by == 'myjobs' or not filter_by:
        query['user_id'] = request.user['username']

    return Queue().get(query)


@view_config(route_name='queue', request_param='last_updated', renderer='json', xhr=True)
def update_queue(request):
    # make sure the get requests are here and there.
    i = 0
    last_updated = request.GET['last_updated']
    queued_items = pull_queued_items(request)
    new_queued_items = []

    for queued_item in queued_items:
        queued_item = queued_items[i]

        # If job is already completed/failed
        if queued_item['status'] in ['complete', 'failed']:
            queued_item['log'] = get_log(queued_item['id'])

        # render the queued_item
        # render the damn thing client side.
        queued_item['html'] = render('doula:templates/queue/queued_item.html',
                                     {'queued_item': queued_item})

        # If the job has not been displayed on the interface yet
        if queued_item['time_started'] > int(last_updated):
            new_queued_items.append(queued_item)
        i += 1

    # sort all of the items with respect to time
    new_queued_items = sorted(new_queued_items, key=lambda k: k['time_started'])

    return {'success': True,
            'queuedItems': queued_items,
            'newQueuedItems': new_queued_items}
