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


def search_queue(request):
    """
    Search for the latest jobs on the queue
    """
    service = get_service_for_query(request)
    jobs_started_after = int(request.params.getone('jobs_started_after'))
    job_ids = json.loads(request.params.getone('job_ids'))

    jobs = []

    for job in query_queue(request):
        # Only return the job if a new job (the start time is after the
        # jobs_started_after time value) or the job is listed in the
        # jobs_and_statuses dictionary
        if job['time_started'] > jobs_started_after or job['id'] in job_ids:
            if service == False or job['service'] == service:
                # If job is already completed/failed
                if job['status'] in ['complete', 'failed']:
                    job['log'] = get_log(job['id'])

                # render the job
                # alextodo. change the queue_item to job everywhere.
                job['html'] = render('doula:templates/queue/queued_item.html',
                                      {'queued_item': job})

                jobs.append(job)

    # sort jobs with respect to time
    jobs = sorted(jobs, key=lambda k: k['time_started'])

    return {
        'success': True,
        'jobs': jobs
    }


def get_service_for_query(request):
    if request.params.getone('service'):
        return request.params.getone('service')
    else:
        return False


def query_queue(request):
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


# New way to query the queue
@view_config(route_name='queue', request_param='jobs_started_after', renderer='json', xhr=True)
def query_queue_view(request):
    response = {'success': True}
    queue = Queue()

    bucket_id = request.params.getone('bucket_id')
    last_updated = request.params.getone('last_updated')
    last_updated = last_updated if last_updated else 0

    if queue.has_bucket_changed(bucket_id, last_updated):
        # Pull the bucket from queue. If it doesn't exist the queue
        # will build one and return the new bucket
        query = build_query_from_request(request)
        query_bucket = queue.get_query_bucket(bucket_id, query)

        for job in query_bucket['jobs']:
            # If job is already completed/failed
            if job['status'] in ['complete', 'failed']:
                job['log'] = get_log(job['id'])

            # render the job
            # alextodo. change the queue_item to job everywhere.
            job['html'] = render('doula:templates/queue/queued_item.html',
                                  {'queued_item': job})

        # sort jobs according to time
        query_bucket['jobs'] = sorted(query_bucket['jobs'], key=lambda k: k['time_started'])

        response['query_bucket'] = query_bucket
        response['has_changed'] = True
    else:
        response['has_changed'] = False

    return response


def build_query_from_request(request):
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

    return query
