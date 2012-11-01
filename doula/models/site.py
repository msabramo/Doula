from doula.cache import Redis
from doula.models.site_tag_history import SiteTagHistory
from doula.util import dirify
from fabric.api import *
from git import *
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

        for app_name, app in self.services.iteritems():
            app_status_value = status_values[app.get_status()]

            if app_status_value > status_value:
                status_value = app_status_value
                self.status = app.get_status()

        return self.status

    def tag(self, tag_history_path, tag_history_remote, tag, msg, user):
        sth = SiteTagHistory(tag_history_path, tag_history_remote, self.name_url, 'output.log')
        sth.tag_site(tag, msg, self.services)

    ############################
    # Lock/Unlock Logic for Site
    ############################

    def is_locked(self):
        """
        Returns true or false based on whether or not the site has been
        locked by an Doula admin
        """
        redis = Redis.get_instance()
        key = 'doula.site.locked:%s' % self.name_url

        if redis.get(key) == 'true':
            return True
        else:
            return False

    def lock(self):
        """
        Lock down a site so no one except an admin can release to the site
        """
        redis = Redis.get_instance()
        key = 'doula.site.locked:%s' % self.name_url
        redis.set(key, 'true')

    def unlock(self):
        """
        Unlock site so everyone can release to the site
        """
        redis = Redis.get_instance()
        key = 'doula.site.locked:%s' % self.name_url
        redis.set(key, 'false')
