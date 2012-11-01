from doula.cache import Redis
from doula.util import *
from fabric.api import *
from git import *
import logging
import simplejson as json
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
    def __init__(self, name, site_name, url, ip,
            config={}, changed_files=[], supervisor_service_names=[]):
        self.name = name
        self.name_url = dirify(name)
        self.site_name = site_name
        self.url = url
        self.ip = ip
        self.config = config
        self.changed_files = changed_files
        self.supervisor_service_names = supervisor_service_names

        self.errors = []

    def pull_services(self):
        """
        Return the services for this node as json
        """
        try:
            return pull_url(self.url + '/services')
        except Exception as e:
            from doula.models.doula_dal import DoulaDAL

            # If we're not able to contact a bambino we unregister
            # the bambino. The Bambino will need to re register itself.
            # when it come back online
            # unregister needs a dict with node name and site only
            node = {'site': self.site_name, 'name': self.name}
            dd = DoulaDAL()
            dd.unregister_node(node)

            vals = (self.url + '/services', e.message)
            msg = 'Unable to contact Bambino at %s because of error %s' % vals
            log.error(msg)

            return None

    def pull_services_as_dicts(self):
        """
        Pull the services from the bambino then return as dicts
        """
        pulled_services = self.pull_services()

        if pulled_services:
            return json.loads(pulled_services)
        else:
            return {}

    def load_services(self):
        """
        Update the services
        """
        # ALEXTODO. HERE IS A BIG CHANGE FOR THE ENTIRE APP
        try:
            self.errors = []
            self.services = {}
            services_as_json = self._get_services_as_json()

            if services_as_json:
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
        redis = Redis.get_instance()
        services_as_json = redis.get('node:services:' + self.name_url)

        if services_as_json == None or services_as_json == 'None':
            services_as_json = self.pull_services()

            if services_as_json:
                redis.set('node:services:' + self.name_url, services_as_json)

        return services_as_json
