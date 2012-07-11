from doula.models.service import Service
from doula.util import *
from fabric.api import *
from git import *
from doula.cache import Cache
import json
import logging
import traceback

# Defines the Data Models for Doula and Bambino.
#
# sites
#   Site
#     nodes
#       services
#         Service
#           packages
#             Package
#     services
#       Service
#         packages
#           Package

log = logging.getLogger('doula')


class Node(object):
    def __init__(self, name, site_name, url, services={}):
        self.name = name
        self.name_url = dirify(name)
        self.site_name = site_name
        self.url = url
        self.services = services
        self.errors = []

    def pull_services(self):
        """
        Return the services for this node as json
        """
        return pull_url(self.url + '/services')

    def load_services(self):
        """
        Update the services
        """
        try:
            self.errors = []
            self.services = {}
            services_as_json = self._get_services_as_json()
            services = json.loads(services_as_json)

            for app in services['services']:
                a = Service.build_app(self.site_name, self.name, self.url, app)
                self.services[a.name_url] = a
        except Exception as e:
            msg = 'Unable to load services. Error: {0}'.format(e.message)
            log.error(msg)
            log.error(traceback.format_exc())

            self.errors.append(msg)

        return self.services

    def _get_services_as_json(self):
        """
        Get the services as json from redis. If not in redis. pull from
        Bambinos
        """
        cache = Cache.cache()
        services_as_json = cache.get('node_services_' + self.name_url)

        if services_as_json:
            return services_as_json
        else:
            return self.pull_services
