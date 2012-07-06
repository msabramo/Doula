from doula.models.service import Service
from doula.util import dirify
from fabric.api import *
from git import *
import json
import logging
import requests
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

    def load_services(self):
        """
        Update the services
        """
        try:
            self.errors = []
            self.services = {}

            r = requests.get(self.url + '/services')
            # If the response is non 200, we raise an error
            r.raise_for_status()
            rslt = json.loads(r.text)

            for app in rslt['services']:
                a = Service.build_app(self.site_name, self.name, self.url, app)
                self.services[a.name_url] = a

        except requests.exceptions.ConnectionError as e:
            msg = 'Unable to contact node {0} at URL {1}'.format(self.name, self.url)
            log.error(msg)
            self.errors.append(msg)
        except Exception as e:
            msg = 'Unable to load services. Error: {0}'.format(e.message)
            log.error(msg)
            tb = traceback.format_exc()
            print 'TRACEBACK'
            print tb

            self.errors.append(msg)

        return self.services
