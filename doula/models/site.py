from doula.cache import Redis
from doula.util import dirify
import logging

log = logging.getLogger('doula')


class Site(object):
    """
    A site represents an Monkey Test Environment. It holds references to
    the nodes that make it up and the services that encompass the entire site.

    The nodes are a dict, for example:
        nodes = {
            "node_name": Node Object
        }

    The services are a dict, for example:
        services = {
            "service_name": Service Object
        }
    """
    def __init__(self, name, status='unknown', nodes={}, services={}):
        self.name = name
        self.name_url = dirify(name)
        self.status = status
        self.nodes = nodes
        self.services = services
        self.redis = Redis.get_instance()

    ################################
    # Status and Tag Logic
    ################################

    def get_status(self):
        """
        The status of the site is the most serious status of all it's services.
        The more serious the status, the higher the status value number.
        """
        status_value = 0
        status_values = {
            'unknown': 0,
            'deployed': 1,
            'tagged': 2,
            'change_to_config': 3,
            'change_to_app': 3,
            'change_to_app_and_config': 3,
            'uncommitted_changes': 4
        }

        for service_name, service in self.services.iteritems():
            service_status_value = status_values[service.get_status()]

            if service_status_value > status_value:
                status_value = service_status_value
                self.status = service.get_status()

        return self.status

    ############################
    # Lock/Unlock Logic for Site
    ############################

    def is_locked(self):
        """
        Returns true or false based on whether or not the site has been
        locked by an Doula admin
        """
        key = 'doula.site.locked:%s' % self.name_url

        if self.redis.get(key) == 'true':
            return True
        else:
            return False

    def lock(self):
        """
        Lock down a site so no one except an admin can release to the site
        """
        key = 'doula.site.locked:%s' % self.name_url
        self.redis.set(key, 'true')

    def unlock(self):
        """
        Unlock site so everyone can release to the site
        """
        key = 'doula.site.locked:%s' % self.name_url
        self.redis.set(key, 'false')



