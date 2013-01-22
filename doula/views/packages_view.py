from doula.config import Config
from doula.models.package import Package
from doula.queue import Queue
from doula.util import dumps
from doula.util import next_version
from pyramid.renderers import render
from pyramid.view import view_config
import logging
import math
import re
import time

log = logging.getLogger(__name__)

###############
# Package Views
###############


@view_config(route_name='packages', renderer="packages/index.html")
def packages_view(request):
    sm_packages = Package.get_sm_packages()
    # show jobs in the past hour 8 hours
    jobs_started_after = math.floor(time.time() - (60 * 60 * 8))

    return {
        'config': Config,
        'sm_packages': sm_packages,
        'queued_items': [],
        'jobs_started_after': jobs_started_after
    }


@view_config(route_name='build_new_package_modal', renderer="packages/build_new_package_modal.html")
def build_new_package_modal(request):
    package = Package.get_sm_package_by_name(request.GET['name'])
    current_version = package.get_current_version()

    return {
        'package': package,
        'current_version': current_version,
        'next_version': next_version(current_version)
    }


@view_config(route_name='build_new_package', renderer="string")
def build_new_package(request):
    site_name = request.GET.get('site_name', '')
    service_name = request.GET.get('service_name', '')

    package = Package.get_sm_package_by_name(request.GET['name'])
    branch = request.GET.get('branch', '')
    # The next version number is a combination of the actual version
    # number and the name of the actual branch
    next_version = request.GET.get('next_version', '') + '-' + branch
    remote = package.get_github_info()['ssh_url']

    errors = validate_package_release(package, branch, next_version)

    if len(errors) == 0:
        job_dict = enqueue_push_package(request.user['username'],
                                        site_name,
                                        service_name,
                                        package,
                                        remote,
                                        branch,
                                        next_version)
    else:
        msg = "There were errors attempting to build new package %s" % (package.name)
        html = render('doula:templates/packages/build_new_package_modal_error.html',
                {'msg': msg, 'errors': errors})

        return dumps({'success': False, 'msg': msg, 'html': html})

    return dumps({'success': True, 'job': job_dict})


def validate_package_release(package, branch, next_version):
    """
    Validate that:
        The version number does not already exists
        The version number doesn't have an @ sign
        The version number isn't empty
    """
    errors = []

    if not next_version:
        errors.append('Version number cannot be empty')

    if next_version.find('@') > -1:
        errors.append('You cannot include the "@" symbol in a version')

    if next_version in package.get_versions():
        errors.append('This version already exist')

    # Ensure the tags don't already exist
    git_info = package.get_github_info()

    for tag in git_info['tags']:
        # tags by doula are always prefixed with a v
        # and test that it doesn't match without
        tag_name = re.sub(r'^v', '', str(tag['name']))

        if tag_name == next_version:
            errors.append('This version already exist')

    return errors


def enqueue_push_package(user_id, site_name, service_name, package, remote, branch, version):
    """
    Enqueue the job onto the queue
    """
    job_dict = {
        'user_id': user_id,
        'site': site_name,
        'service': service_name,
        'package_name': package.name,
        'comparable_name': package.comparable_name,
        'remote': remote,
        'branch': branch,
        'version': version,
        'job_type': 'build_new_package'
    }

    q = Queue()
    job_id = q.this(job_dict)
    job_dict['id'] = job_id

    return job_dict
