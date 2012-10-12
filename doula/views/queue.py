from doula.config import Config
from doula.log import get_log
from doula.queue import Queue
from doula.views.helpers import *
from pyramid.renderers import render
from pyramid.view import view_config


# QUEUE VIEWS
@view_config(route_name='queue', renderer='queue/index.html')
def show_queue(request):
    return {
        'config': Config,
        'jobs_started_after': 0
    }


@view_config(route_name='queue', request_param='jobs_started_after', renderer='json', xhr=True)
def search_queue(request):
    """
    Search for the latest jobs on the queue
    """
    service = False

    if request.params.getone('service'):
        service = request.params.getone('service')

    jobs_started_after = int(request.params.getone('jobs_started_after'))
    job_ids = json.loads(request.params.getone('job_ids'))

    queued_items = []

    for item in pull_queued_items(request):
        # Only return the job if a new item (the start time is after the
        # jobs_started_after time value) or the job is listed in the
        # jobs_and_statuses dictionary
        if item['time_started'] > jobs_started_after or item['id'] in job_ids:
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
    query = {
        'job_type': [
            'push_to_cheeseprism',
            'cycle_services',
            'push_service_environment']
        }

    if not request.params.getone('filter_by') == 'alljobs':
        query['user_id'] = request.user['username']

    if request.params.getone('sort_by'):
        if request.params.getone('sort_by') != 'all':
            query['status'] = request.params.getone('sort_by')

    if request.params.getone('site'):
        query['site'] = request.params.getone('site')

    if request.params.getone('service'):
        query['service'] = request.params.getone('service')

    return Queue().get(query)
