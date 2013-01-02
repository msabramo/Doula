from doula.config import Config
from doula.models.node import Node
from doula.models.package import Package
from doula.models.release import Release
from doula.models.service_config_dal import ServiceConfigDAL
from doula.models.service_config import ServiceConfig
from doula.helper_filters import formatted_github_day_and_time
from doula.models.tag import Tag
from doula.util import *
from fabric.api import *
from socket import error as socket_error
import logging
import re
import requests
import xmlrpclib

log = logging.getLogger('doula')


class Service(object):
    # Service attributes are same as dict
    # "current_branch_app": "mt3",
    # "change_count_app": 0,
    # "change_count_config": 0,
    # "remote": "git@code.corp.surveymonkey.com:AppEnv/anweb.git",
    # "name": "anweb",
    # "tags": [
    #     {
    #         "date": 1334013665,
    #         "message": "all the kings horses",
    #         "name": "x.2"
    #     }
    # ],
    # "is_dirty_app": true,
    # "last_tag_message": "all the kings horses",
    # "is_dirty_config": true,
    # "status": "uncommitted_changes",
    # "last_tag_config": "x.2",
    # "changed_files": [
    #     "bin/activate.csh"
    # ],
    # "last_tag_app": "x.2",
    # "packages": {
    #     "repoze.lru": {
    #         "version": "0.3",
    #         "name": "repoze.lru"
    #     },
    #     "pyramid": {
    #         "version": "1.2.7",
    #         "name": "pyramid"
    #     }
    # },
    # "config": {
    #     date: "2011-07-18 15:08:55 -0700",
    #     sha: "1df6e091b5251dadcb0e8e7671c30438653264b9",
    #     changed_files: {
    #       setup.sh: "deleted",
    #       README.rst: "deleted",
    #       app.ini: "deleted",
    #        supervisor.conf: "deleted",
    #       .gitignore: "deleted"
    #     },
    #     branch: "mt3",
    #     author: "Whit"
    # },
    # "current_branch_config": "mt3",
    # "supervisor_service_names": []
    # }

    def __init__(self, **dict_data):
        self.__dict__.update(dict_data)
        self.name_url = dirify(self.name)

        self.nodes = {}

        self.config['formatted_date'] = formatted_github_day_and_time(self.config['date'])
        self._add_packages(dict_data['packages'])
        self._add_tags_from_service_dict(dict_data['tags'])
        self.last_tag = self._get_last_tag()

    def append_node(self, node, service_as_dict):
        """
        Create new node object and append it to the nodes dict

        We get passed an existing site node object and a the service as a dict
        that was returned from Bambino.
        """
        self.nodes[node.name] = Node(node.name,
                                     node.site_name,
                                     node.url,
                                     node.ip,
                                     service_as_dict['config'],
                                     service_as_dict['changed_files'],
                                     service_as_dict['supervisor_service_names'])

    @staticmethod
    def report_status(results):
        for result in results:
            logging.info('port: %s, status: %s' % (result['name'], result['description']))

    @staticmethod
    def cycle(proxy, service_name):
        try:
            logging.info('stopping %s' % service_name)
            results = proxy.supervisor.stopProcessGroup(service_name)
            Service.report_status(results)

            logging.info('starting %s' % service_name)
            results = proxy.supervisor.startProcessGroup(service_name)
            Service.report_status(results)

            success = True

            for result in results:
                if(result['status'] != 80):
                    success = False

            if(success):
                True
            else:
                raise CycleServiceException('one service failed', results)

        # exceptions are weird with xmlrpc: http://betabug.ch/blogs/ch-athens/1012
        except (socket_error, xmlrpclib.Fault, xmlrpclib.ProtocolError, xmlrpclib.ResponseError), error_code:
            raise CycleServiceException(error_code)

    def is_config_up_to_date(self):
        """
        Check if any of the nodes for this service are
        out of date.
        """
        for node_name, node in self.nodes.iteritems():
            # If any node is not up to date. the entire service
            # is out of date.
            if not node.config["is_up_to_date"]:
                return False

        return True

    def get_releases(self):
        """
        Return the releases for this service to this site
        """
        return Release.get_releases(self.site_name, self.name)

    def get_configs(self):
        """
        Return the ServiceConfig's for this service to this site

        Returns a list of ServiceConfig objects.
        """
        sc_dal = ServiceConfigDAL()
        service_configs = sc_dal.get_service_configs(Config.get_safe_site(self.site_name), self.name)

        # check if the service sha is in the service_configs list
        found_service_config = False

        if not found_service_config:
            # Since we did not find the current service_config
            config_dict = self.config.copy()
            config_dict['site'] = self.site_name
            config_dict['service'] = self.name
            service_configs.append(ServiceConfig(**config_dict))

        return service_configs

    def _add_packages(self, pckgs):
        """
        Add package objects from the Bambino dict
        """
        self.packages = {}

        for package_name, package_as_dict in pckgs.iteritems():
            package = Package(package_as_dict['name'], package_as_dict['version'], '')
            self.packages[package.comparable_name] = package

    def _add_tags_from_service_dict(self, tags_as_dicts):
        self.tags = []

        for tag in tags_as_dicts:
            self.tags.append(Tag(tag['name'], tag['date'], tag['message']))

        self._update_last_tag()

    def get_compare_url(self):
        """
        Use the remote url to return the GitHub Comapre view URL.
        The GitHub Compare URL has the format:
        http://<GITHUB_URL>/<USER>/<REPO>/compare/<START>...<END>
        For us this means
        http://code.corp.surveymonkey.com/DevOps/[name]/compare/[last_tag_app]...[current_branch_app]
        """
        if self.remote.startswith('http'):
            # parses http://code.corp.surveymonkey.com/tbone/anweb.git type remote
            m = re.search(r'http:\/\/([\w\.]+)\/([\w\d]+)\/([\w\d]+)', self.remote)
        else:
            # parses git@code.corp.surveymonkey.com:tbone/anweb-1.git type remote
            m = re.search(r'@([\w\.]+):([\w\d]+)\/([\w\d]+)', self.remote)

        compare_url = ''

        if m:
            compare_url = 'http://' + m.group(1) + '/' + m.group(2) + '/' + self.name
            compare_url += '/compare/' + self.last_tag.name + '...' + self.current_branch_app

        return compare_url

    def tag(self, tag, msg, user):
        """
        Tag the current service
        """
        payload = {'tag': tag, 'description': msg, 'apps': self.name}
        r = requests.post(self.url + '/tag', data=payload)
        # If the response is non 200, we raise an error
        r.raise_for_status()

        self.tag = tag
        self.msg = msg
        self.status = 'tagged'

    def _update_last_tag(self):
        self.last_tag_app = self._get_last_tag()
        self.last_tag_config = self._get_last_tag()

    def _get_last_tag(self):
        # Initialize an empty tag if it doesn't tag exist
        latest_tag = Tag('', '', '')
        latest_tag_date = 0

        for tag in self.tags:
            if tag.date > latest_tag_date:
                latest_tag = tag
                latest_tag_date = tag.date

        return latest_tag

    def get_status(self):
        return self.status

    def next_version(self):
        """
        Get the next logical version.
        i.e. 0.2.4 -> 0.2.5
        """
        return next_version(self.last_tag.name)

    def get_tag_by_name(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag

        return False

    def get_package_by_name(self, package_name):
        package = False

        for pckg in self.packages:
            if pckg.comparable_name == comparable_name(package_name):
                package = pckg
                break

        return package

    def freeze_requirements(self):
        reqs = ''
        sorted_packages = sorted(self.packages.iterkeys())

        for name in sorted_packages:
            pckg = self.packages[name]
            reqs += pckg.name + '==' + pckg.version + "\n"

        return reqs


class CycleServiceException(Exception):
    def __init__(self, message, results=[]):
        self.message = message
        self.results = results

    def __str__(self):
        return dumps({'message': self.message, 'results': self.results})
