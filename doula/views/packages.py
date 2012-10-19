from doula.config import Config
from doula.models.package import Package
from pyramid.view import view_config
import math
import logging
import time

log = logging.getLogger(__name__)

###############
# Package Views
###############


@view_config(route_name='packages', renderer="packages/index.html")
def service(request):
    sm_packages = Package.get_sm_packages()
    # show jobs in the past hour 8 hours
    jobs_started_after = math.floor(time.time() - (60 * 60 * 8))

    return {
        'config': Config,
        'sm_packages': sm_packages,
        'queued_items': [],
        'jobs_started_after': jobs_started_after
    }
