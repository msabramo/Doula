from doula.models.node import Node
from doula.models.site_tag_history import SiteTagHistory
from doula.util import dirify
from fabric.api import *
from git import *
import logging

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


class Site(object):
    def __init__(self, name, status='unknown', nodes={}, services={}):
        self.name = name
        self.name_url = dirify(name)
        self.status = status
        self.nodes = nodes
        self.services = services

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

    def get_logs(self):
        all_logs = []

        for app_name, app in self.services.iteritems():
            all_logs.extend(app.get_logs())

        return all_logs

    def tag(self, tag_history_path, tag_history_remote, tag, msg, user):
        # alextodo, need to move this logic into the site object
        # alextodo, figure out the output.log file, where should
        # it actually go? will you read it?
        # create a global config object. this will also allow me to test. config[]
        sth = SiteTagHistory(tag_history_path, tag_history_remote, self.name_url, 'output.log')
        sth.tag_site(tag, msg, self.services)

    @staticmethod
    def build_site(simple_site):
        """
        Take the simple dictionary version of a site object, i.e.
            {name:value, nodes[{'name':value, 'site':value, 'url':value}]}
        and return an actual Site object with all the nodes and services
        built as well.
        """
        site = Site(simple_site['name'])
        site.nodes = Site._build_nodes(simple_site['nodes'])
        site.services = Site._get_combined_services(site.nodes)

        return site

    @staticmethod
    def _build_nodes(simple_nodes):
        """
        Takes the nodes with format:
            nodes[{'name':value, 'site':value, 'url':value}]
        And builds Node objects
        """
        nodes = {}

        for name, n in simple_nodes.iteritems():
            node = Node(name, n['site'], n['url'])
            node.load_services()
            nodes[name] = node

        return nodes

    @staticmethod
    def _get_combined_services(nodes):
        """
        Takes the nodes (contains actual Node objects) and
        builds the services as a combined list of their
        services for the entire site.
        """
        combined_services = {}

        for k, node in nodes.iteritems():
            for app_name, app in node.services.iteritems():
                combined_services[app_name] = app

        return combined_services
