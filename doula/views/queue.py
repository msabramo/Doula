from doula.config import Config
from doula.log import get_log
from doula.queue import Queue
from doula.views.helpers import *
from pyramid.renderers import render
from pyramid.view import view_config


# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    query = {'job_type': ['push_to_cheeseprism', 'cycle_services', 'push_service_environment']}
    # alextodo. abstract this code into a single function, used in search queue
    sort_by = request.params.get('sort_by')
    if sort_by == 'complete' or sort_by == 'failed' or sort_by == 'queued':
        query['status'] = sort_by

    # Filter by filters by username, or all users
    filter_by = request.params.get('filter_by')

    if filter_by == 'myjobs' or not filter_by:
        query['user_id'] = request.user['username']

    queued_items = []

    for item in Queue().get(query):
        item['log'] = ''
        # If job is already completed/failed
        if item['status'] in ['complete', 'failed']:
            item['log'] = get_log(item['id'])

        queued_items.append(item)

    # sort all of the items with respect to time
    queued_items = sorted(queued_items, key=lambda k: k['time_started'])
    # descending order
    # alextodo. put this int he template
    queued_items = reversed(queued_items)

    return {
        'config': Config,
        'queued_items': queued_items,
        'jobs_started_after': 0
    }


@view_config(route_name='queue', request_param='jobs_started_after', renderer='json', xhr=True)
def search_queue(request):
    """
    Search for the latest jobs on the queue
    """
    service = request.params.getone('service')

    if service == 'false':
        service = False

    jobs_started_after = int(request.params.getone('jobs_started_after'))
    jobs_and_statuses = json.loads(request.params.getone('jobs_and_statuses'))
    jobs_and_statuses_keys = jobs_and_statuses.keys()

    queued_items = []

    for item in pull_queued_items(request):
        # Only return the job if a new item (the start time is after the
        # jobs_started_after time value) or the job is listed in the
        # jobs_and_statuses dictionary
        if item['time_started'] > jobs_started_after or item['id'] in jobs_and_statuses_keys:
            if service == False or item['service'] == service:
                # If job is already completed/failed
                if item['status'] in ['complete', 'failed']:
                    item['log'] = get_log(item['id'])

                # render the item
                item['html'] = render('doula:templates/queue/queued_item.html',
                                      {'queued_item': item})

                queued_items.append(item)

    # sort all of the items with respect to time
    queued_items = sorted(queued_items, key=lambda k: k['time_started'])

    return {
        'success': True,
        'queuedItems': queued_items
    }


def pull_queued_items(request):
    filter_by = request.params.getone('filter_by')

    query = {
        'job_type': [
            'push_to_cheeseprism',
            'cycle_services',
            'push_service_environment']
        }

    if filter_by == 'myjobs' or not filter_by:
        query['user_id'] = request.user['username']

    return Queue().get(query)
