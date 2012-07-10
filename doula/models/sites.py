from contextlib import contextmanager
from doula.models.audit import Audit
from doula.models.site_tag_history import SiteTagHistory
from doula.models.sites_dal import SiteDAL
from doula.services.cheese_prism import CheesePrism
from doula.services.cheese_prism import PythonPackage
from doula.util import dirify
from doula.util import dumps
from doula.util import is_number
from fabric.api import *
from git import *
from tempfile import TemporaryFile

import json
import logging
import operator
import re
import requests
import shutil
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


class Service(object):
    def __init__(self, name, site_name, node_name, url,
        current_branch_app='', current_branch_config='',
        change_count_app='', change_count_config='',
        is_dirty_app=False, is_dirty_config=False,
        last_tag_app='', last_tag_config='', last_tag_message='',
        status='', remote='', repo='', packages=[], changed_files=[], tags=[]):
        self.name = name
        self.site_name = site_name
        self.node_name = node_name
        self.name_url = dirify(name)
        self.url = url

        self.current_branch_app = current_branch_app
        self.current_branch_config = current_branch_config

        self.change_count_app = change_count_app
        self.change_count_config = change_count_config

        self.is_dirty_app = is_dirty_app
        self.is_dirty_config = is_dirty_config

        self.last_tag_app = last_tag_app
        self.last_tag_config = last_tag_config
        self.last_tag_message = last_tag_message

        self.status = status
        self.remote = remote
        self.packages = packages
        self.changed_files = changed_files
        self.tags = tags

    @staticmethod
    def build_app(site_name, node_name, url, app):
        """Build an service object from the app dictionary"""

        a = Service(app['name'], site_name, node_name, url)
        a.current_branch_app = app['current_branch_app']
        a.change_count_app = app['change_count_app']
        a.change_count_config = app['change_count_config']
        a.is_dirty_config = app['is_dirty_config']
        a.last_tag_config = app['last_tag_config']
        a.status = app['status']
        a.remote = app['remote']
        a.last_tag_app = app['last_tag_app']
        a.last_tag_message = app['last_tag_message']
        a.current_branch_config = app['current_branch_config']
        a.changed_files = app['changed_files']
        a.tags = []
        a.packages = []
        a.add_packages(app['packages'])
        a.add_tags_from_dict(app['tags'])
        a.last_tag = a.get_last_tag()

        return a

    def add_packages(self, pckgs):
        for name, pckg in pckgs.iteritems():
            self.packages.append(Package(pckg['name'], pckg['version']))

    def add_tags_from_dict(self, tags_as_dicts):
        for tag in tags_as_dicts:
            self.tags.append(Tag(tag['name'], tag['date'], tag['message']))

        self._update_last_tag()

    def get_compare_url(self):
        """
        Use the remote url to return the Github Comapre view URL.
        The Github Compare URL has the format:
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

        audit = Audit()
        audit.log_action(self.site_name, self.name, 'tag', user)

    def _update_last_tag(self):
        self.last_tag_app = self.get_last_tag()
        self.last_tag_config = self.get_last_tag()

    def get_last_tag(self):
        # Initialize an empty tag if it doesn't tag exist
        latest_tag = Tag('', '', '')
        latest_tag_date = 0

        for tag in self.tags:
            if tag.date > latest_tag_date:
                latest_tag = tag
                latest_tag_date = tag.date

        return latest_tag

    def get_status(self):
        if self.status == 'tagged' and SiteDAL.is_deployed(self, self.last_tag):
            return 'deployed'
        else:
            return self.status

    def mark_as_deployed(self, tag, user):
        """
        Mark an service as deployed
        """
        self.status = 'deployed'
        SiteDAL.save_service_as_deployed(self, tag)

        audit = Audit()
        audit.log_action(self.site_name, self.name, 'deploy', user)

    def get_logs(self):
        audit = Audit()
        app_logs = audit.get_app_logs(self.site_name, self.name)

        for log in app_logs:
            log['service'] = self.name

        return app_logs

    def next_version(self):
        """
        Get the next logical version.
        i.e. 0.2.4 -> 0.2.5
        """
        next_version = ''
        rslts = re.split(r'(\d+)', self.last_tag.name)
        rslts.reverse()
        found_digit = False

        for rslt in rslts:
            if found_digit is False and is_number(rslt):
                found_digit = True
                part = int(rslt) + 1
            else:
                part = rslt

            next_version = str(part) + next_version

        return next_version

    def get_tag_by_name(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag

        return False

    def freeze_requirements(self):
        reqs = ''

        self.packages.sort(key=operator.attrgetter('name'))

        for pckg in self.packages:
            reqs += pckg.name + '==' + pckg.version + "\n"

        return reqs


class Package(object):
    """
    Represents a python package
    """
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def get_versions(self):
        pypackage = CheesePrism.find_package_by_name(self.name)
        versions = pypackage.get_versions() if pypackage else []

        if not self.version in versions:
            versions.append(self.version)

        return versions

    def distribute(self, branch, new_version):
        with self.repo() as repo:
            self.update_version(repo, new_version)
            self.commit(repo, ['setup.py'], 'DOULA: Updating Version.')
            self.push(repo, "origin")
            self.upload(repo)

    @contextmanager
    def repo(self):
        try:
            # Where all of the cloned repos are placed
            if not os.path.exists('repos'):
                os.mkdir('repos')
            repo_path = os.path.join('repos', self.name)

            # Clone specified service's repo
            repo = Repo.clone_from("git@code.corp.surveymonkey.com:joed/%s.git" % self.name,
                                   repo_path)
            yield repo
        finally:
            # Clean up repo directory
            shutil.rmtree(repo.working_dir)

    def update_version(self, repo, new_version):
        # Alter setup.py to match the new version
        setup_py_path = os.path.join(repo.working_dir, 'setup.py')
        with open(setup_py_path, 'r+') as f:
            tmp = TemporaryFile()

            for line in f.readlines():
                if line.startswith("version"):
                    line = "version = '%s'\n" % new_version
                tmp.write(line)

            # Go back to the beginning of each file
            tmp.seek(0)
            f.seek(0)

            f.write(tmp.read())

    def commit(self, repo, files, msg):
        # Commit change to repo
        index = repo.index
        index.add(files)
        index.commit(msg)

    def push(self, repo, remote):
        # Push changes
        origin = repo.remotes[remote]
        origin.pull()
        origin.push()

    def upload(self, repo):
        # Call `python setup.py sdist upload` to put upload to cheeseprism
        with lcd(repo.working_dir):
            local('python setup.py sdist upload -r local')


class Tag(object):
    """
    Represents a git tag
    """
    def __init__(self, name, date, message):
        self.name = name
        self.date = date
        self.message = message
